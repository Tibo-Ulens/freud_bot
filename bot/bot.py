import logging
import psycopg2
from contextlib import suppress

import discord
from discord.ext import commands


logger = logging.getLogger("bot")


class Bot(commands.Bot):
    """Custom discord bot class"""

    def __init__(self, pg_conn, *args, **kwargs):
        self.pg_conn = pg_conn

        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls) -> "Bot":
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

        conn = psycopg2.connect(
            user="postgres_user",
            password="postgres_password",
            host="freud_bot_db",
            port="5432",
            database="freud_bot",
        )

        cursor = conn.cursor()

        verified_user_table_query = """
        CREATE TABLE IF NOT EXISTS verified_user (
            discord_id        TEXT NOT NULL UNIQUE,
            email             TEXT NOT NULL UNIQUE,
            confirmation_code TEXT          UNIQUE
        );
        """
        cursor.execute(verified_user_table_query)
        conn.commit()

        return cls(conn, command_prefix="$", intents=intents)

    def load_extensions(self) -> None:
        """Load all enabled extensions"""

        from bot.extensions import EXTENSIONS

        for ext in EXTENSIONS:
            logger.info(f"Loading extension {ext}")
            self.load_extension(ext)

    def add_cog(self, cog: commands.Cog) -> None:
        """Add a cog to the bot"""

        logger.info(f"Adding cog {cog.qualified_name}")
        super().add_cog(cog)

    def add_command(self, command: commands.Command) -> None:
        """Add a command to the bot"""

        logger.info(f"Adding command {command.qualified_name}")
        super().add_command(command)

    async def login(self, *args, **kwargs):
        """Create a connector and setup sessions before logging in to Discord"""

        await super().login(*args, **kwargs)

    async def close(self) -> None:
        """Close the Discord connection, aiohttp session, connector, and resolver"""

        # Remove all extensions and cogs
        for ext in list(self.extensions):
            with suppress(Exception):
                logger.info(f"Unloading extensions {ext}")
                self.unload_extension(ext)

        for cog in list(self.cogs):
            with suppress(Exception):
                logger.info(f"Removing cog {cog}")
                self.remove_cog(cog)

        logger.info("Closing bot client...")

        await super().close()

        await self.logout()

    async def on_error(self, event: str, *args, **kwargs) -> None:
        logger.exception(f"Unhandled exception in {event}")
