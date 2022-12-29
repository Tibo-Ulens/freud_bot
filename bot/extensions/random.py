from discord import app_commands, Interaction

from bot.bot import Bot
from bot.extensions import ErrorHandledCog


class Random(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="mommy",
        description="For when somebody likes their mother a little *too* much",
    )
    async def mommy(self, ia: Interaction):
        await ia.response.send_message(
            "The Oedipus complex is a phase in the life of a young boy in which he wishes to have sex with his mother"
        )


async def setup(bot: Bot):
    await bot.add_cog(Random(bot))
