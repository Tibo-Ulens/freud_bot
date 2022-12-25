import asyncio
from contextlib import closing
import csv
import datetime
from datetime import timedelta, datetime as DateTime
from io import BytesIO
import logging
from time import sleep
from typing import Iterator

from cairosvg import svg2png
from discord import app_commands, Interaction, File
from discord.app_commands import errors
from discord.ext.commands import Cog
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

from bot import constants
from bot.bot import Bot
from bot.constants import day_to_planner
from bot.models.course import Course
from bot.models.enrollment import Enrollment
from bot.models.lecture import Lecture
from bot.util import course_autocomplete, check_has_manage_guild


logger = logging.getLogger("bot")
web_logger = logging.getLogger("selenium")


def get_csv_links(course_code: str) -> Iterator[str]:
    """Select a course in TimeEdit given its code and get the csv download links for it"""

    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    for time_idx in range(1, 5):
        driver.get(constants.TIMEEDIT_URL)
        driver.find_element(
            By.CSS_SELECTOR, f".linklist a:nth-of-type({time_idx})"
        ).click()

        web_logger.info(f"searching timestep: {time_idx}")

        # Search by course
        type_select = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "select#fancytypeselector")
            )
        )
        type_select = Select(type_select)

        # VERY IMPORTANT BUT DON'T ASK WHY
        for opt in type_select.options:
            opt.get_attribute("innerHTML")
            opt.click()

        type_select.select_by_visible_text("Cursus")

        # Search for and add each course
        search = driver.find_element(By.CSS_SELECTOR, "input#ffsearchname")
        search.clear()
        search.send_keys(course_code)
        search.send_keys(Keys.ENTER)

        web_logger.info(f"sought for course {course_code}")
        sleep(0.5)
        try:
            add_btn = WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "#objectbasketitemX0")
                )
            )
        except TimeoutException:
            web_logger.info("not found, skipping")
            continue

        add_btn.click()

        web_logger.info(f"added course {course_code}")

        # Show the calendar
        show_btn = driver.find_element(By.CSS_SELECTOR, "input#objectbasketgo")
        show_btn.click()

        csv_btn = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.formatLinksItem[title='CSV']")
            )
        )
        href = csv_btn.get_attribute("href")

        web_logger.info("done")

        yield href

    driver.close()
    driver.quit()


class Calendar(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    group = app_commands.Group(name="course", description="course management")

    @staticmethod
    async def store_lecture_info(course_code: str, course_name: str, ia: Interaction):
        """
        Scrape and store the lecture info for a given course
        """

        logger.info(f"finding lecture info for course [{course_code}] {course_name}")
        await ia.edit_original_response(
            content=f"finding lecture info for course {course_name} (this may take a while)..."
        )

        try:
            csv_urls = [url for url in get_csv_links(course_code)]
        except Exception as err:
            logger.error(err)
            await ia.edit_original_response(
                content="Something went wrong, please contact a server admin"
            )
            return

        logger.info(
            f"downloading lecture info for course [{course_code}] {course_name}"
        )
        await ia.edit_original_response(
            content=f"downloading lecture info for course {course_name}"
        )

        create_lecture_futures = []

        for csv_url in csv_urls:
            with closing(
                requests.get(csv_url, allow_redirects=True, stream=True)
            ) as req:
                line_generator = (
                    line.decode("utf-8") for line in req.iter_lines(chunk_size=1024)
                )

                # UGent csv files start with:
                next(line_generator)  # an empty line (?)
                next(line_generator)  # the UGent name
                next(line_generator)  # course info

                reader = csv.DictReader(line_generator, delimiter=",")

                for entry in reader:
                    create_lecture_futures.append(Lecture.from_csv_entry(entry))

        logger.info(f"storing lecture info for course [{course_code}] {course_name}")
        await ia.edit_original_response(
            content=f"storing lecture info for course {course_name}"
        )
        await asyncio.gather(*create_lecture_futures)

    @app_commands.command(
        name="calendar",
        description="Show your personal calendar for this week",
    )
    async def calendar(self, ia: Interaction):
        enrollments = await Enrollment.find_for_profile(str(ia.user.id))

        if not enrollments:
            await ia.response.send_message(
                "You are not enrolled in any courses, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        courses: list[Course] = await asyncio.gather(
            *[Course.find_by_code(e.course_id) for e in enrollments]
        )
        course_codes: list[str] = list(map(lambda c: c.code, courses))

        await ia.response.send_message("Building calendar overview...", ephemeral=True)

        today = datetime.date.today()
        week_nr = today.isocalendar()[1]
        week_start = today - timedelta(days=today.weekday() % 7)
        week_days = [
            (week_start + timedelta(days=n)).strftime("%d-%m-%Y") for n in range(7)
        ]

        # Create the dictionary from week_days so that every date is present,
        # not just ones that have items
        # {date: [{course}, {course}, ...], ...}
        week_info_dict: dict[DateTime, list[dict[str, str]]] = {
            day: list() for day in week_days
        }
        for course_code in course_codes:
            course_lectures = await Lecture.find_for_course(course_code)

            for lecture in course_lectures:
                if lecture.start_date in week_days:
                    week_info_dict[lecture.start_date].append(lecture.__dict__)

        week_info = list(week_info_dict.items())

        # week_info must be sorted as the svg arguments are simply indexed from
        # 0 to 6
        week_info.sort(
            key=lambda i: datetime.datetime.strptime(i[0], "%d-%m-%Y").date()
        )

        week_planners = {
            f"planner{i}": day_to_planner(i, day_info[1])
            for [i, day_info] in enumerate(week_info)
        }

        labeled_week_days = {f"date{i}": d for [i, d] in enumerate(week_days)}
        filled_svg = constants.CALENDAR_TEMPLATE.format(
            week=week_nr, **labeled_week_days, **week_planners
        )

        png_bytes = svg2png(bytestring=bytes(filled_svg, "utf-8"), write_to=None)
        png_virt_file = BytesIO(initial_bytes=png_bytes)
        png_file = File(png_virt_file, filename="calendar.png")

        await ia.edit_original_response(content="", attachments=[png_file])

    @app_commands.guild_only()
    @group.command(name="enroll", description="Enroll in a specific course")
    @app_commands.describe(name="The name of the course to enroll in")
    @app_commands.autocomplete(name=course_autocomplete)
    async def enroll_in_course(self, ia: Interaction, name: str):
        course = await Course.find_by_name(name)

        if course is None:
            await ia.response.send_message(
                f"Course {name} does not exist, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        if await Enrollment.find(str(ia.user.id), str(course.code)):
            await ia.response.send_message(
                f"You are already enrolled in [{str(course.code)}] {name}, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        await Enrollment.create(profile_id=str(ia.user.id), course_id=str(course.code))

        logger.info(
            f"[{ia.user.id}] {ia.user.name} enrolled in course [{str(course.code)}] {name}"
        )
        await ia.response.send_message(
            f"You have enrolled in the course [{str(course.code)}] {name}",
            ephemeral=True,
        )

    @app_commands.guild_only()
    @group.command(name="drop", description="Drop a specific course")
    @app_commands.describe(name="The name of the course to drop")
    @app_commands.autocomplete(name=course_autocomplete)
    async def drop_course(self, ia: Interaction, name: str):
        course = await Course.find_by_name(name)

        enrollment = await Enrollment.find(str(ia.user.id), str(course.code))

        if enrollment is None:
            await ia.response.send_message(
                "You are not enrolled in this course, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        await enrollment.delete()

        logger.info(
            f"[{ia.user.id}] {ia.user.name} dropped course [{str(course.code)}] {name}"
        )
        await ia.response.send_message(
            f"You have dropped the course [{str(course.code)}] {name}", ephemeral=True
        )

    @app_commands.guild_only()
    @group.command(name="overview", description="Show all courses you are enrolled in")
    async def show_enrolled(self, ia: Interaction):
        enrollments = await Enrollment.find_for_profile(str(ia.user.id))

        if not enrollments:
            await ia.response.send_message(
                "You are not enrolled in any courses, if you think this is a mistake please contact a server admin",
                ephemeral=True,
            )
            return

        courses: list[Course] = await asyncio.gather(
            *[Course.find_by_code(enr.course_id) for enr in enrollments]
        )
        courses = list(map(lambda c: f"[{c.code}] {c.name}", courses))

        await ia.response.send_message("\n".join(courses), ephemeral=True)

    @app_commands.guild_only()
    @group.command(name="add", description="Add a new course to the list of courses")
    @app_commands.checks.has_role("Moderator")
    @app_commands.describe(code="The course code of the new course")
    @app_commands.describe(name="The full name of the new course")
    async def add_course(self, ia: Interaction, code: str, name: str):
        course = await Course.find_by_name(name)
        if course is not None:
            await ia.response.send_message(
                f"A course with the name {name} already exists, if you think this is a mistake please contact a server admin"
            )
            return

        await Course.create(code=code, name=name)

        logger.info(f"scraping lectures for course [{code}] {name}")
        await ia.response.send_message(f"scraping lectures for course [{code}] {name}")
        await self.store_lecture_info(code, name, ia)

        logger.info(f"added course [{code}] {name}")
        await ia.edit_original_response(content=f"Added course [{code}] {name}")

    @app_commands.guild_only()
    @group.command(name="remove", description="Remove an available course")
    @app_commands.checks.has_role("Moderator")
    @app_commands.describe(name="The name of the course to remove")
    @app_commands.autocomplete(name=course_autocomplete)
    async def remove_course(self, ia: Interaction, name: str):
        course = await Course.find_by_name(name)
        if course is None:
            await ia.response.send_message(
                f"A course with the name {name} does not exist, if you think this is a mistake please contact a server admin"
            )
            return

        await course.delete()

        logger.info(f"removed course [{str(course.code)}] {name}")
        await ia.response.send_message(f"Removed course [{course.code}] {name}")

    @app_commands.guild_only()
    @group.command(name="list", description="List all available courses")
    @app_commands.checks.has_role("Moderator")
    async def list_courses(self, ia: Interaction):
        courses = await Course.get_all()
        courses = list(map(lambda c: f"[{c.code}] {c.name}", courses))

        if courses:
            await ia.response.send_message("\n".join(courses))
        else:
            await ia.response.send_message("No courses found")

    @app_commands.guild_only()
    @app_commands.check(check_has_manage_guild)
    @group.command(name="refresh", description="Refresh the lecture info for a course")
    @app_commands.autocomplete(name=course_autocomplete)
    async def course_refresh(self, ia: Interaction, name: str):
        course = await Course.find_by_name(name)
        if course is None:
            await ia.response.send_message(
                f"A course with the name {name} does not exist, if you think this is a mistake please contact a server admin"
            )
            return

        logger.info(
            f"deleting old lecture info for course [{course.code}] {course.name}"
        )
        await ia.response.send_message(
            f"Deleting old lecture info for course {course.name}"
        )
        lectures = await Lecture.find_for_course(course.code)
        await asyncio.gather(*[l.delete() for l in lectures])

        await self.store_lecture_info(course.code, course.name, ia)
        logger.info(f"refreshed lecture info [{course.code}] {course.name}")
        await ia.edit_original_response(
            content=f"Refreshed lecture info for course {course.name}"
        )

    @add_course.error
    @remove_course.error
    @list_courses.error
    @course_refresh.error
    async def handle_command_error(self, ia: Interaction, error):
        if isinstance(error, errors.MissingRole) or isinstance(
            error, errors.MissingPermissions
        ):
            logger.warn(f"[{ia.user.id}] {ia.user.name} used moderator command")
            await ia.followup.send(
                content="You are not allowed to use this command", ephemeral=True
            )
        else:
            logger.error(error)
            await ia.followup.send(
                content="Unknown error, please contact a server admin"
            )


async def setup(bot: Bot):
    await bot.add_cog(Calendar(bot))
