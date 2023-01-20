import asyncio
from datetime import datetime
import json
import logging
from logging import Handler, LogRecord, Formatter, Filter

import discord
from discord import Embed, Colour, Interaction
from discord.ext.commands import Context

from bot.models.config import Config
from bot import util


class DiscordHandler(Handler):
    """Log handler that writes log messages to a discord text channel"""

    def __init__(self, filter_target: str):
        super().__init__()
        self.setFormatter(
            Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        self.addFilter(Filter(filter_target))
        self.setLevel(logging.WARNING)

        self.loop = asyncio.get_event_loop()

    def emit(self, record: LogRecord) -> None:
        self.loop.create_task(self.send_embed(record))

    async def send_embed(self, record: LogRecord):
        if hasattr(record, "__interaction__"):
            record_interaction: Interaction = record.__interaction__
            record_guild = record_interaction.guild
        elif hasattr(record, "__context__"):
            record_context: Context = record.__context__
            record_guild = record_context.guild
        else:
            return

        if record_guild is None:
            return

        guild_config = await Config.get(record_guild.id)

        tag_msg = ""
        if (
            (record.levelno == logging.ERROR or record.levelno == logging.WARNING)
            and guild_config is not None
            and guild_config.admin_role is not None
        ):
            admin_role = discord.utils.get(
                record_guild.roles, id=guild_config.admin_role
            )
            tag_msg = util.render_role(admin_role)

        if guild_config is not None and guild_config.logging_channel is not None:
            logging_channel = record_guild.get_channel(guild_config.logging_channel)

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
