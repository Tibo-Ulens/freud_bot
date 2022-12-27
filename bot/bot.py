import asyncio
import os
from contextlib import suppress

import logging
import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from bot.events.bot import BotEvent as BotEvent


logger = logging.getLogger("bot")


class Bot(commands.Bot):
    """Custom discord bot class"""

    def __init__(self, db: AsyncEngine, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    @classmethod
    async def create(cls) -> "Bot":
        """Create and return a new bot instance"""

        intents = discord.Intents.default()
        intents.message_content = True
        intents.bans = False

        intents.dm_messages = False
        intents.reactions = False
        intents.typing = False

        intents.integrations = False
        intents.invites = False
        intents.members = False
        intents.presences = False
        intents.voice_states = False

        intents.webhooks = False

        pg_engine = create_async_engine(os.environ.get("DB_URL"), echo=False)
        logger.info(BotEvent.DatabaseConnected())

        return cls(db=pg_engine, command_prefix="$", intents=intents)

    async def load_extensions(self) -> None:
        """Load all enabled extensions"""

        from bot.extensions import EXTENSIONS

        for ext in EXTENSIONS:
            await self.load_extension(ext)
            logger.info(BotEvent.ExtensionLoaded(ext))

    async def add_cog(self, cog: commands.Cog) -> None:
        """Add a cog to the bot"""

        await super().add_cog(cog)
        logger.info(BotEvent.CogAdded(cog.qualified_name))

    async def close(self) -> None:
        # Remove all extensions
        extension_tasks = []
        for ext in list(self.extensions):
            with suppress(Exception):
                extension_tasks.append(self.unload_extension(ext))
                logger.debug(BotEvent.ExtensionUnloaded(ext))

        await asyncio.gather(*extension_tasks)

        # Remove all cogs
        cog_tasks = []
        for cog in list(self.cogs):
            with suppress(Exception):
                cog_tasks.append(self.remove_cog(cog))
                logger.debug(BotEvent.CogRemoved(cog.qualified_name))

        await asyncio.gather(*cog_tasks)

        await super().close()
        logger.info(BotEvent.ClientClosed())

        await self.db.dispose()
        logger.info(BotEvent.DatabaseClosed())

        await self.logout()
        logger.info(BotEvent.Exited())

    async def on_error(self, event: str) -> None:
        logger.exception(f"Unhandled exception in {event}")
