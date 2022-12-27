import random
import logging

from discord import Message, Guild
from discord.ext.commands import Cog

from bot import constants, root_logger
from bot.bot import Bot
from bot.events.bot import BotEvent as BotEvent
from bot.discord_logger import DiscordHandler
from bot.models.config import Config


logger = logging.getLogger("bot")


class Listeners(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        logger.info(BotEvent.Ready())

    @Cog.listener()
    async def on_guild_available(self, guild: Guild):
        logger.info(f"guild {guild.name} available")

        guild_config = await Config.get(guild.id)
        if guild_config is None or guild_config.logging_channel is None:
            return

        logging_channel = guild.get_channel(guild_config.logging_channel)
        discord_handler = DiscordHandler(channel=logging_channel, filter_target="bot")
        self.bot.discord_handler = discord_handler
        root_logger.addHandler(discord_handler)

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
