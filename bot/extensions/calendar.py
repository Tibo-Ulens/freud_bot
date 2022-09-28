import logging

import discord
from discord import app_commands, Interaction
from discord.app_commands import errors
from discord.ext.commands import Cog
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

from bot.bot import Bot


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
    courses = ["math", "art", "science", "history"]
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

    @group.command(name="add", description="Add a new course to the list of courses")
    @app_commands.checks.has_role("Moderator")
    @app_commands.describe(code="The course code for the new course")
    @app_commands.describe(name="The full name of the new course")
    async def add(self, iactn: Interaction, code: str, name: str):
        logger.info(f"adding course '{name}' with code '{code}'")

        await iactn.response.send_message("WIP")

    @group.command(
        name="remove", description="Remove a course from the list of courses"
    )
    @app_commands.checks.has_role("Moderator")
    @app_commands.autocomplete(course=course_autocomplete)
    async def remove(self, iactn: Interaction, course: str):
        logger.info(f"removing course '{course}'")

        await iactn.response.send_message("WIP")

    @add.error
    @remove.error
    async def handle_command_error(self, iactn: Interaction, error):
        if isinstance(error, errors.MissingRole):
            await iactn.response.send_message(
                "You are not allowed to use this command", ephemeral=True
            )


async def setup(bot: Bot):
    await bot.add_cog(Calendar(bot))
