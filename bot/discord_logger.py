import asyncio
from datetime import datetime
import json
import logging
from logging import Handler, LogRecord, Formatter, Filter

from discord import TextChannel, Embed, Colour


class DiscordHandler(Handler):
    """Log handler that writes log messages to a discord text channel"""

    def __init__(self, channel: TextChannel, filter_target: str):
        super().__init__()
        self.setFormatter(
            Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        self.addFilter(Filter(filter_target))
        self.setLevel(logging.INFO)

        self.channel = channel
        self.loop = asyncio.get_event_loop()

    def emit(self, record: LogRecord) -> None:
        self.loop.create_task(self.send_embed(record))

    async def send_embed(self, record: LogRecord):
        embed = self.format_embed(record)
        await self.channel.send(embed=embed)

    def format_embed(self, record: LogRecord) -> Embed:
        embed = Embed()
        embed.colour = self.level_to_colour(record.levelno)

        event_timestamp = datetime.strptime(record.asctime, "%Y-%m-%d %H:%M:%S,%f")
        event_timestamp = event_timestamp.strftime("%Y-%m-%d %H:%M:%S")

        embed.add_field(name="timestamp", value=event_timestamp, inline=True)

        if record.levelno == logging.ERROR:
            embed.add_field(name="error", value=record.message, inline=False)
        else:
            [event, args] = record.message.split(" | ")
            scope = event.split(".")[0]
            event = event.split(".")[1]
            args: dict[str, str] = json.loads(args)

            embed.add_field(name="scope", value=scope, inline=True)
            embed.add_field(name="event", value=event, inline=True)
            for k, v in args.items():
                embed.add_field(name=k, value=v, inline=False)

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
