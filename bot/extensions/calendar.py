import asyncio
from collections import defaultdict
from contextlib import closing
import json
import logging
from time import sleep

import csv
from discord import app_commands, Interaction
from discord.app_commands import errors
from discord.ext.commands import Cog
import requests
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from bot.bot import Bot
from bot.models.course import Course
from bot.models.enrollment import Enrollment


TIMEEDIT_URL = "https://cloud.timeedit.net/ugent/web/guest/"


logger = logging.getLogger("bot")
web_logger = logging.getLogger("selenium")
cache_logger = logging.getLogger("cache")


def levenshtein_ratio(s1: str, s2: str) -> int:
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(
                    1
                    + min((distances[index1], distances[index1 + 1], newDistances[-1]))
                )
        distances = newDistances

    return distances[-1] / max(len(s1), len(s2))


async def course_autocomplete(
    _: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    courses = await Course.get_all()
    courses = list(map(lambda c: c.name, courses))
    courses.sort(key=lambda c: levenshtein_ratio(c, current))

    return [app_commands.Choice(name=course, value=course) for course in courses]


def get_csv_link(course_codes: list[str]) -> str:
    """Build up the timeedit calendar and get the csv file download link for it"""

    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(TIMEEDIT_URL)
    driver.find_element(By.CSS_SELECTOR, ".linklist a").click()

    # Search by course
    type_select = WebDriverWait(driver, 2).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "select#fancytypeselector"))
    )
    type_select = Select(type_select)

    # VERY IMPORTANT BUT DON'T ASK WHY
    for opt in type_select.options:
        opt.get_attribute("innerHTML")
        opt.click()

    type_select.select_by_visible_text("Cursus")

    # Search for and add each course
    search = driver.find_element(By.CSS_SELECTOR, "input#ffsearchname")
    for code in course_codes:
        search.clear()
        search.send_keys(code)
        search.send_keys(Keys.ENTER)

        web_logger.info(f"sought for course {code}")
        sleep(0.5)
        add_btn = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#objectbasketitemX0"))
        )
        add_btn.click()

        web_logger.info(f"added course {code}")

    # Show the calendar
    show_btn = driver.find_element(By.CSS_SELECTOR, "input#objectbasketgo")
    show_btn.click()

    csv_btn = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a.formatLinksItem[title='CSV']")
        )
    )
    href = csv_btn.get_attribute("href")

    driver.close()
    driver.quit()

    web_logger.info("done")

    return href


class Calendar(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="course", description="course management")

    async def maybe_update_cache(self, course_codes: list[str], iactn: Interaction):
        """
        Check if the cache is missing info on the given list of courses and if
        so, add it
        """

        # Gotta decode here cuz redis returns bytestrings
        stored_courses: set[str] = set(
            [course.decode("utf-8") async for course in self.bot.redis.scan_iter()]
        )

        missing_courses = list(set(course_codes) - stored_courses)

        if not missing_courses:
            return

        cache_logger.info(f"updating cache for courses {' '.join(missing_courses)}")
        await iactn.edit_original_response(
            content="Updating cache: finding course data (this may take a while)..."
        )

        try:
            csv_url = get_csv_link(missing_courses)
        except Exception as err:
            cache_logger.error(err)
            await iactn.edit_original_response(
                content="Something went wrong, please contact a server admin"
            )
            return

        await iactn.edit_original_response(
            content="Updating cache: downloading course data..."
        )

        with closing(requests.get(csv_url, allow_redirects=True, stream=True)) as req:
            line_content = (
                line.decode("utf-8") for line in req.iter_lines(chunk_size=1024)
            )

            # UGent csv files start with:
            next(line_content)  # an empty line (?)
            next(line_content)  # the UGent name
            next(line_content)  # course info

            reader = csv.DictReader(line_content, delimiter=",")

            mapped_course_info = list(
                map(
                    lambda i: {
                        "start_date": i["Start datum"],
                        "type": i["Aard"],
                        "name": i["Cursuscode,Naam"],
                        "lecturer": i["Lesgever"],
                        "location": i["Lokaal,Gebouw,Campus"],
                    },
                    reader,
                )
            )

        # Group the courses by course code so they're easier to retrieve
        grouped_course_info: defaultdict[str, list[str]] = defaultdict(list)

        for info in mapped_course_info:
            grouped_course_info[info["name"].split(".")[0]].append(json.dumps(info))

        await iactn.edit_original_response(
            content="Updating cache: storing course data..."
        )

        async with self.bot.redis.pipeline(transaction=True) as pipe:
            for (name, info) in grouped_course_info.items():
                pipe.lpush(name, *info)

            await pipe.execute()

    @app_commands.command(
        name="calendar",
        description="Show your personal calendar for this week",
    )
    async def calendar(self, iactn: Interaction):
        enrollments = await Enrollment.find_for_profile(str(iactn.user.id))

        if not enrollments:
            await iactn.response.send_message(
                "You are not enrolled in any courses, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        courses: list[Course] = await asyncio.gather(
            *[Course.find_by_code(e.course_id) for e in enrollments]
        )
        courses: list[str] = list(map(lambda c: c.code, courses))

        await iactn.response.send_message(
            "Building calendar overview...", ephemeral=True
        )

        await self.maybe_update_cache(courses, iactn)

        found = await self.bot.redis.exists(courses[0])
        logger.info(f"found {found} matches")

    @app_commands.guild_only()
    @group.command(name="enroll", description="Enroll in a specific course")
    @app_commands.describe(name="The name of the course to enroll in")
    @app_commands.autocomplete(name=course_autocomplete)
    async def enroll_in_course(self, iactn: Interaction, name: str):
        course = await Course.find_by_name(name)

        if course is None:
            await iactn.response.send_message(
                f"Course {name} does not exist, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        if await Enrollment.find(str(iactn.user.id), str(course.code)):
            await iactn.response.send_message(
                f"You are already enrolled in [{str(course.code)}] {name}, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        await Enrollment.create(
            profile_id=str(iactn.user.id), course_id=str(course.code)
        )

        logger.info(
            f"[{iactn.user.id}] {iactn.user.name} enrolled in course [{str(course.code)}] {name}"
        )
        await iactn.response.send_message(
            f"You have enrolled in the course [{str(course.code)}] {name}",
            ephemeral=True,
        )

    @app_commands.guild_only()
    @group.command(name="drop", description="Drop a specific course")
    @app_commands.describe(name="The name of the course to drop")
    @app_commands.autocomplete(name=course_autocomplete)
    async def drop_course(self, iactn: Interaction, name: str):
        course = await Course.find_by_name(name)

        enrollment = await Enrollment.find(str(iactn.user.id), str(course.code))

        if enrollment is None:
            await iactn.response.send_message(
                "You are not enrolled in this course, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        await enrollment.delete()

        logger.info(
            f"[{iactn.user.id}] {iactn.user.name} dropped course [{str(course.code)}] {name}"
        )
        await iactn.response.send_message(
            f"You have dropped the course [{str(course.code)}] {name}", ephemeral=True
        )

    @app_commands.guild_only()
    @group.command(name="overview", description="Show all courses you are enrolled in")
    async def show_enrolled(self, iactn: Interaction):
        enrollments = await Enrollment.find_for_profile(str(iactn.user.id))

        if not enrollments:
            await iactn.response.send_message(
                "You are not enrolled in any courses, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        courses: list[Course] = await asyncio.gather(
            # *[(lambda e: Course.find_by_code(e.course_id))(enr) for enr in enrollments]
            *[Course.find_by_code(enr.course_id) for enr in enrollments]
        )
        courses = list(map(lambda c: f"[{c.code}] {c.name}", courses))

        await iactn.response.send_message("\n".join(courses), ephemeral=True)

    @app_commands.guild_only()
    @group.command(name="add", description="Add a new course to the list of courses")
    @app_commands.checks.has_role("Moderator")
    @app_commands.describe(code="The course code for the new course")
    @app_commands.describe(name="The full name of the new course")
    async def add_course(self, iactn: Interaction, code: str, name: str):
        course = await Course.find_by_name(name)
        if course is not None:
            await iactn.response.send_message(
                f"A course with the name {name} already exists, if you think this is a mistake please contact a server admin"
            )
            return

        await Course.create(code=code, name=name)

        logger.info(f"added course [{code}] {name}")
        await iactn.response.send_message(f"Added course [{code}] {name}")

    @app_commands.guild_only()
    @group.command(name="remove", description="Remove an available course")
    @app_commands.checks.has_role("Moderator")
    @app_commands.describe(name="The name of the course to remove")
    @app_commands.autocomplete(name=course_autocomplete)
    async def remove_course(self, iactn: Interaction, name: str):
        course = await Course.find_by_name(name)
        if course is None:
            await iactn.response.send_message(
                f"A course with the name {name} does not exist, if you think this is a mistake please contact a server admin"
            )

        await course.delete()

        logger.info(f"removed course [{str(course.code)}] {name}")
        await iactn.response.send_message(f"Removed course [{course.code}] {name}")

    @app_commands.guild_only()
    @group.command(name="list", description="List all available courses")
    @app_commands.checks.has_role("Moderator")
    async def list_courses(self, iactn: Interaction):
        courses = await Course.get_all()
        courses = list(map(lambda c: f"[{c.code}] {c.name}", courses))

        if courses:
            await iactn.response.send_message("\n".join(courses))
        else:
            await iactn.response.send_message("No courses found")

    @add_course.error
    @remove_course.error
    @list_courses.error
    async def handle_command_error(self, iactn: Interaction, error):
        if isinstance(error, errors.MissingRole):
            logger.warn(f"[{iactn.user.id}] {iactn.user.name} used moderator command")
            await iactn.response.send_message(
                "You are not allowed to use this command", ephemeral=True
            )
        else:
            logger.error(error)
            await iactn.response.send_message("Unknown error")


async def setup(bot: Bot):
    await bot.add_cog(Calendar(bot))
