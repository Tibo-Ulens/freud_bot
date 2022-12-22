import os
from contextlib import suppress

import logging
import discord
from discord.ext import commands
import redis.asyncio as redis
from redis.asyncio import Redis


logger = logging.getLogger("bot")


class Bot(commands.Bot):
    """Custom discord bot class"""

    def __init__(self, redis: Redis, *args, **kwargs):
        self.redis = redis
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

        redis_conn = redis.Redis(
            host=os.environ.get("CACHE_HOST"), port=os.environ.get("CACHE_PORT")
        )
        await redis_conn.ping()

        logger.info("Cache connection established")

        return cls(command_prefix="$", intents=intents, redis=redis_conn)

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
        # Remove all extensions and cogs
        for ext in list(self.extensions):
            with suppress(Exception):
                logger.info(f"Unloading extensions {ext}")
                self.unload_extension(ext)

        for cog in list(self.cogs):
            with suppress(Exception):
                logger.info(f"Removing cog {cog}")
                self.remove_cog(cog)

        logger.info("Closing redis connection")
        await self.redis.close()

        logger.info("Closing bot client...")

        await super().close()

        await self.logout()

    async def on_error(self, event: str) -> None:
        logger.exception(f"Unhandled exception in {event}")
