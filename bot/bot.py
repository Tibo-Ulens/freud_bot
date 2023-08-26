import asyncio
import os
from contextlib import suppress

import logging
from logging import Logger
import discord
from discord.ext import commands

# from bot.events.bot import BotEvent as BotEvent
from bot.log.guild_adapter import GuildAdapter


logger = logging.getLogger("bot")


class Bot(commands.Bot):
    """Custom discord bot class"""

    def __init__(self, *args, **kwargs):
        self.logger: Logger = None
        self.discord_logger: GuildAdapter = None
        super().__init__(*args, **kwargs)

    @classmethod
    async def create(cls) -> "Bot":
        """Create and return a new bot instance"""

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = False

        intents.bans = False
        intents.dm_messages = False
        intents.integrations = False
        intents.invites = False
        intents.reactions = False
        intents.typing = False
        intents.voice_states = False
        intents.webhooks = False

        return cls(command_prefix="$", intents=intents)

    async def load_extensions(self) -> None:
        """Load all enabled extensions"""

        from bot.extensions import EXTENSIONS

        for ext in EXTENSIONS:
            await self.load_extension(ext)
            logger.debug(f"loaded extension '{ext}'")

    async def add_cog(self, cog: commands.Cog) -> None:
        """Add a cog to the bot"""

        await super().add_cog(cog)
        logger.debug(f"added cog '{cog.qualified_name}'")

    async def close(self) -> None:
        # Remove all extensions
        extension_tasks = []
        for ext in list(self.extensions):
            with suppress(Exception):
                extension_tasks.append(self.unload_extension(ext))
                logger.debug(f"unloaded extension '{ext}'")

        await asyncio.gather(*extension_tasks)

        # Remove all cogs
        cog_tasks = []
        for cog in list(self.cogs):
            with suppress(Exception):
                cog_tasks.append(self.remove_cog(cog))
                logger.debug(f"removed cog '{cog.qualified_name}'")

        await asyncio.gather(*cog_tasks)

        await super().close()
        logger.info("client closed")

        await self.db.dispose()
        logger.info("database closed")

        logger.info("bot exited")

    async def on_error(self, event: str) -> None:
        logger.exception(f"Unhandled exception in {event}")
