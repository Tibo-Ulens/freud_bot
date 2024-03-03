from discord import app_commands, Interaction, Embed
from discord.app_commands import Choice

from bot.bot import Bot
from bot.decorators import check_user_is_verified
from bot import constants
from bot.extensions import ErrorHandledCog


class Drive(ErrorHandledCog):
    @app_commands.command(
        name="drive",
        description="Send a link to a Google Drive folder",
    )
    @app_commands.describe(folder="The name of the link")
    @app_commands.choices(
        folder=[
            Choice(name="1e Bachelor", value="1"),
            Choice(name="2e Bachelor", value="2"),
            Choice(name="Nuttige Info", value="3"),
        ]
    )
    @check_user_is_verified()
    async def drive(self, ia: Interaction, folder: Choice[str]):
        embed = Embed(
            title="",
            description=f"[{folder.name}]({constants.DRIVE_LINKS[folder.name]})",
        )
        await ia.response.send_message(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Drive(bot))
