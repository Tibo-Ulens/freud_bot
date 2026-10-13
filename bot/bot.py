import asyncio
from contextlib import suppress
import importlib.util
import logging
from logging import Logger
import os
from typing import Sequence

import discord
from discord.abc import Snowflake
from discord.ext import commands
from discord.utils import MISSING
import redis.asyncio as redis

from bot.log.guild_adapter import GuildAdapter


logger = logging.getLogger("bot")


async def members_intent_enabled(token: str) -> bool:
    """
    Check if the server members intent is enabled for this application

    Discord refuses the connection when asking for a privileged intent that
    isn't enabled, so this has to be checked before connecting
    """

    client = discord.Client(intents=discord.Intents.none())
    try:
        await client.login(token)
        flags = (await client.application_info()).flags
    finally:
        await client.close()

    return flags.gateway_guild_members or flags.gateway_guild_members_limited


class Bot(commands.Bot):
    """Custom discord bot class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger: Logger = None
        self.discord_logger: GuildAdapter = None
        self.loop = asyncio.get_running_loop()

        self.redis = redis.Redis.from_url(os.environ["CH_URL"], decode_responses=True)
        logger.info("cache connected")

    @classmethod
    async def create(cls, token: str) -> "Bot":
        """Create and return a new bot instance"""

        intents = discord.Intents.default()

        # Privileged and only granted after Discord reviews the bot. Without
        # it new members aren't greeted and have to use /verify themselves
        intents.members = await members_intent_enabled(token)
        if not intents.members:
            logger.warning(
                "the server members intent is not enabled, running without it"
            )

        # Privileged, and not needed: Discord still sends the content of
        # messages that mention the bot, which is all we use it for
        intents.message_content = False
        intents.auto_moderation = False
        intents.emojis_and_stickers = False
        intents.integrations = False
        intents.invites = False
        intents.moderation = False
        intents.typing = False
        intents.voice_states = False
        intents.webhooks = False

        return cls(command_prefix=commands.when_mentioned, intents=intents)

    async def load_extensions(self) -> None:
        """Load all enabled extensions"""

        from bot.extensions import EXTENSIONS

        for ext in EXTENSIONS:
            await self.load_extension(ext)
            logger.info(f"loaded extension '{ext}'")

    async def start_tasks(self) -> None:
        """Start all bot-related tasks"""

        from bot.tasks import TASKS

        await self._async_setup_hook()

        for task in TASKS:
            await self._start_task(task)
            logger.info(f"started task '{task}'")

    async def _start_task(self, name: str):
        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ImportError(f"Task {name} not found")

        lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lib)

        setup = getattr(lib, "setup")
        await setup(self)

    async def add_cog(
        self,
        cog: commands.Cog,
        /,
        *,
        override: bool = False,
        guild: Snowflake | None = MISSING,
        guilds: Sequence[Snowflake] = MISSING,
    ) -> None:
        """Add a cog to the bot"""

        await super().add_cog(cog, override=override, guild=guild, guilds=guilds)
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

        await self.redis.aclose()
        logger.info("cache closed")

        await self.db.dispose()
        logger.info("database closed")

        logger.info("bot exited")

    async def on_error(self, event: str) -> None:
        logger.exception(f"Unhandled exception in {event}")
