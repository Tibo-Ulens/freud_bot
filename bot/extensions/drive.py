from discord import app_commands, Interaction
from discord.app_commands import Choice
from discord.ext.commands import Cog

from bot.bot import Bot
from bot import constants


class Drive(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="drive",
        description="Send a link to the Google Drive folder for a specific course",
    )
    @app_commands.describe(course="The name of the course to link to")
    @app_commands.choices(
        course=[
            Choice(name="Grondslagen van de Psychologie", value=""),
            Choice(name="Kwalitatieve Data Analyse", value=""),
            Choice(name="Ontwikkelingspsychologie", value=""),
            Choice(name="Sociale Psychologie", value=""),
            Choice(name="Statistiek 1", value=""),
            Choice(name="Algemene Psychologie", value=""),
            Choice(name="Differentiële Psychologie", value=""),
            Choice(name="Erfelijkheidsleer", value=""),
            Choice(name="Introductie Cognitieve Psychologie 1", value=""),
            Choice(name="Methodologie", value=""),
            Choice(name="Maatschappelijke Structuren", value=""),
        ]
    )
    async def drive(self, iactn: Interaction, course: Choice[str]):
        await iactn.response.send_message(f"{constants.DRIVE_LINKS[course.name]}")


async def setup(bot: Bot):
    await bot.add_cog(Drive(bot))
