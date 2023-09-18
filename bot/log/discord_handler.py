import asyncio
from datetime import datetime
import logging
from logging import Handler, LogRecord

from discord import Embed, Colour, Guild

from models.config import Config


class DiscordHandler(Handler):
    """Log handler to route logs to the correct guild"""

    def __init__(self, level: int | str = 0) -> None:
        self.loop = asyncio.get_event_loop()

        super().__init__(level)

    def emit(self, record: LogRecord) -> None:
        self.loop.create_task(self.send_embed(record))

    async def send_embed(self, record: LogRecord) -> None:
        # The GuildAdapter should've stored the guild object in the records __dict__ keys
        if record.__dict__["guild"] is None:
            return

        guild: Guild = record.__dict__["guild"]
        guild_config = await Config.get(guild.id)

        if guild_config is None or guild_config.logging_channel is None:
            return

        logging_channel = guild.get_channel(guild_config.logging_channel)

        # Tag admins on errors
        tag_msg = ""
        if record.levelno == logging.ERROR and guild_config.admin_role is not None:
            admin_role = guild.get_role(guild_config.admin_role)
            tag_msg = admin_role.mention

        embed = self.format_embed(record)
        await logging_channel.send(content=tag_msg, embed=embed)

    def format_embed(self, record: LogRecord) -> Embed:
        embed = Embed()
        embed.colour = self.level_to_colour(record.levelno)
        embed.timestamp = datetime.strptime(record.asctime, "%Y-%m-%d %H:%M:%S,%f")

        embed.title = record.levelname
        embed.description = record.message

        return embed

    @staticmethod
    def level_to_colour(level: int) -> Colour:
        match level:
            case logging.DEBUG:
                return Colour.from_str("#88a8bf")
            case logging.INFO:
                return Colour.from_str("#3fc03f")
            case logging.WARN:
                return Colour.from_str("#fabd2f")
            case logging.ERROR:
                return Colour.from_str("#fb4934")
