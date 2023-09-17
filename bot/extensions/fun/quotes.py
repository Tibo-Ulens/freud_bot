import random
import logging

from discord import Message

from bot import constants
from bot.bot import Bot
from bot.extensions import ErrorHandledCog


logger = logging.getLogger("bot")


class Quotes(ErrorHandledCog):
    @ErrorHandledCog.listener("on_message")
    async def send_quote_if_mentioned(self, msg: Message):
        if msg.author == self.bot.user:
            return

        if self.bot.user in msg.mentions:
            quote = random.choice(constants.FREUD_QUOTES)
            await msg.reply(quote)


async def setup(bot: Bot):
    await bot.add_cog(Quotes(bot))
