import random
import logging

from discord import Message
from discord.ext.commands import Cog

from bot import constants
from bot.bot import Bot
from bot.events.bot import Bot as BotEvent


logger = logging.getLogger("bot")


class Listeners(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        logger.info(BotEvent.Ready())

    @Cog.listener()
    async def on_message(self, msg: Message):
        if self.bot.user.mentioned_in(msg):
            await self.send_random_quote(msg)

    @staticmethod
    async def send_random_quote(msg: Message):
        quote = random.choice(constants.FREUD_QUOTES)
        await msg.reply(quote)


async def setup(bot: Bot):
    await bot.add_cog(Listeners(bot))
