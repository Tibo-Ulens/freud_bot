from discord import Guild

from bot import util
from bot.events import Event


class BotEvent(Event):
    """Events related to the bot itself"""

    def synced_commands(guild: Guild, amount: int) -> Event:
        """Synced slash commands"""

        return Event(
            user_msg=f"Synced {amount} commmands to the current guild",
            log_msg=f"synced {amount} commands to guild {util.render_guild(guild)}",
        )
