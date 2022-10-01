import logging

from discord import app_commands, Interaction
from discord.app_commands import errors
from discord.ext.commands import Cog
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

from bot.bot import Bot
from bot.models.course import Course


TIMEEDIT_URL = "https://cloud.timeedit.net/ugent/web/guest/"


logger = logging.getLogger("bot")


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


class Calendar(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="calendar",
        description="Show your personal calendar for this week",
    )
    async def calendar(self, iactn: Interaction):
        await iactn.response.send_message("thinking...")

        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get("https://wiki.archlinux.org/")

        await iactn.edit_original_response(content="done")

    group = app_commands.Group(name="course", description="calendar stuff")

    @group.command(name="enroll", description="Enroll in a specific course")
    async def enroll(self, iactn: Interaction):
        await iactn.response.send_message("WIP")

    @group.command(name="drop", description="Drop a specific course")
    async def drop(self, iactn: Interaction):
        await iactn.response.send_message("WIP")

    @app_commands.guild_only()
    @group.command(name="add", description="Add a new course to the list of courses")
    @app_commands.checks.has_role("Moderator")
    @app_commands.describe(code="The course code for the new course")
    @app_commands.describe(name="The full name of the new course")
    async def add(self, iactn: Interaction, code: str, name: str):
        logger.info(f"adding course '{name}' with code '{code}'")

        course = await Course.find_by_name(name)
        if course is not None:
            await iactn.response.send_message(f"Course {name} already exists")
            return

        await Course.create(code=code, name=name)

        await iactn.response.send_message(f"Added course [{code}] {name}")

    @app_commands.guild_only()
    @group.command(name="remove", description="Remove an available course")
    @app_commands.checks.has_role("Moderator")
    @app_commands.describe(name="The name of the course to remove")
    @app_commands.autocomplete(name=course_autocomplete)
    async def remove(self, iactn: Interaction, name: str):
        logger.info(f"removing course '{name}'")

        course = await Course.find_by_name(name)
        if course is None:
            await iactn.response.send_message(f"Course {name} does not exist")

        await course.delete()
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

    @add.error
    @remove.error
    @list_courses.error
    async def handle_command_error(self, iactn: Interaction, error):
        if isinstance(error, errors.MissingRole):
            await iactn.response.send_message(
                "You are not allowed to use this command", ephemeral=True
            )
        else:
            logger.error(error)
            await iactn.response.send_message("Unknown error")


async def setup(bot: Bot):
    await bot.add_cog(Calendar(bot))
