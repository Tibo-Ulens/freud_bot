from logging import LoggerAdapter
from typing import Any, MutableMapping

from discord import Guild


class GuildAdapter(LoggerAdapter):
    """Log adapter to insert information about the guild logs should be routed to"""

    def __init__(self, logger: Any) -> None:
        super().__init__(logger)

    def debug(self, msg, *args, guild: Guild, **kwargs) -> None:
        return super().debug(msg, *args, guild=guild, **kwargs)

    def info(self, msg, *args, guild: Guild, **kwargs) -> None:
        return super().info(msg, *args, guild=guild, **kwargs)

    def warning(self, msg, *args, guild: Guild, **kwargs) -> None:
        return super().warning(msg, *args, guild=guild, **kwargs)

    def error(self, msg, *args, guild: Guild, **kwargs) -> None:
        return super().error(msg, *args, guild=guild, **kwargs)

    def critical(self, msg, *args, guild: Guild, **kwargs) -> None:
        return super().critical(msg, *args, guild=guild, **kwargs)

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        if "guild" in kwargs:
            kwargs["extra"] = {"guild": kwargs["guild"]}
            del kwargs["guild"]

        return (msg, kwargs)
