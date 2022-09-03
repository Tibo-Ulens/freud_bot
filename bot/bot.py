import os
from contextlib import suppress

import logging
import discord
from discord.ext import commands
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from bot.constants import GUILD_ID


logger = logging.getLogger("bot")


class Bot(commands.Bot):
    """Custom discord bot class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    async def create(cls) -> "Bot":
        """Create and return a new bot instance"""

        intents = discord.Intents.default()
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

        return cls(command_prefix="$", intents=intents)

    async def setup_hook(self):
        """Sync slash commands to guild"""

        self.tree.copy_global_to(guild=GUILD_ID)
        await self.tree.sync()

    async def load_extensions(self) -> None:
        """Load all enabled extensions"""

        from bot.extensions import EXTENSIONS

        for ext in EXTENSIONS:
            logger.info(f"Loading extension {ext}")
            await self.load_extension(ext)

    async def add_cog(self, cog: commands.Cog) -> None:
        """Add a cog to the bot"""

        logger.info(f"Adding cog {cog.qualified_name}")
        await super().add_cog(cog)

    async def close(self) -> None:
        """Close the Discord connection"""

        # Remove all extensions and cogs
        for ext in list(self.extensions):
            with suppress(Exception):
                logger.info(f"Unloading extensions {ext}")
                self.unload_extension(ext)

        for cog in list(self.cogs):
            with suppress(Exception):
                logger.info(f"Removing cog {cog}")
                self.remove_cog(cog)

        logger.info("Closing Postgres connection")
        self.pg_conn.close()

        logger.info("Closing bot client...")

        await super().close()

        await self.logout()

    async def on_error(self, event: str) -> None:
        logger.exception(f"Unhandled exception in {event}")
