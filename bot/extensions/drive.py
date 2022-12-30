from discord import app_commands, Interaction, Embed
from discord.app_commands import Choice

from bot.bot import Bot
from bot.decorators import check_user_is_verified
from bot import constants
from bot.extensions import ErrorHandledCog


class Drive(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="drive",
        description="Send a link to the Google Drive folder for a specific course",
    )
    @app_commands.describe(course="The name of the course to link to")
    @app_commands.choices(
        course=[
            Choice(name="Grondslagen van de Psychologie", value="1"),
            Choice(name="Kwalitatieve Data Analyse", value="2"),
            Choice(name="Ontwikkelingspsychologie", value="3"),
            Choice(name="Sociale Psychologie", value="4"),
            Choice(name="Statistiek 1", value="5"),
            Choice(name="Algemene Psychologie", value="6"),
            Choice(name="Differentiële Psychologie", value="7"),
            Choice(name="Erfelijkheidsleer", value="8"),
            Choice(name="Introductie Cognitieve Psychologie 1", value="9"),
            Choice(name="Methodologie", value="10"),
            Choice(name="Maatschappelijke Structuren", value="11"),
        ]
    )
    @check_user_is_verified
    async def drive(self, ia: Interaction, course: Choice[str]):
        embed = Embed(
            title="",
            description=f"[{course.name}]({constants.DRIVE_LINKS[course.name]})",
        )
        await ia.response.send_message(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Drive(bot))
