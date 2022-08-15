import random

from discord import Message
from discord.ext.commands import Cog, Context

from bot import constants
from bot.bot import Bot


class Listeners(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_message(self, msg: Message):
        if self.bot.user.mentioned_in(msg):
            await self.send_random_quote(msg)

    @staticmethod
    async def send_random_quote(msg: Message):
        quote = random.choice(constants.FREUD_QUOTES)
        await msg.reply(quote)


def setup(bot: Bot):
    bot.add_cog(Listeners(bot))
