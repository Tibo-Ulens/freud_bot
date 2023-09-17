import logging
from logging import Filter

from discord import Guild

from models.config import Config

from bot import root_logger, util
from bot.bot import Bot
from bot.extensions import ErrorHandledCog

from bot.log.discord_handler import DiscordHandler
from bot.log.guild_adapter import GuildAdapter


logger = logging.getLogger("bot")


class ModLogging(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @ErrorHandledCog.listener()
    async def on_ready(self):
        discord_logger = logging.getLogger("discord")

        handler = DiscordHandler()
        handler.addFilter(Filter("discord"))

        discord_logger.addHandler(handler)

        routed_discord_logger = GuildAdapter(discord_logger)
        routed_discord_logger.setLevel(logging.INFO)
        self.bot.discord_logger = routed_discord_logger

        bot_logger = root_logger.getChild("bot")
        self.bot.logger = bot_logger

        logger.info("ready")

    @ErrorHandledCog.listener()
    async def on_guild_available(self, guild: Guild):
        logger.info(f"guild {util.render_guild(guild)} available")

    @ErrorHandledCog.listener()
    async def on_guild_join(self, guild: Guild):
        logger.info(f"joined guild {util.render_guild(guild)}")
        await Config.create(guild_id=guild.id)
        logger.info(f"created config for guild {util.render_guild(guild)}")


async def setup(bot: Bot):
    await bot.add_cog(ModLogging(bot))
