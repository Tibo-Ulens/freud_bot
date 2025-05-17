from discord import Guild

from bot.events import Event
from bot import util


class ConfigEvent(Event):
    """Configuration related events"""

    @staticmethod
    def missing_config(guild: Guild) -> Event:
        """The guild does not have a config yet"""

        return Event(
            user_msg="The bot has not been set up properly yet, please notify a server admin",
            log_msg=f"missing config for guild {util.render_guild(guild)}",
            error=True,
        )

    @staticmethod
    def missing_config_option(guild: Guild, option: str) -> Event:
        """The guild is missing a config option"""

        return Event(
            user_msg="The bot has not been set up properly yet, please notify a server admin",
            log_msg=f"missing config option '{option}' for guild {util.render_guild(guild)}",
            error=True,
        )
