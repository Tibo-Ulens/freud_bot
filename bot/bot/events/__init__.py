from discord import Member, User
from discord.app_commands import Command

from bot import util


class Event:
    """
    Parent class for logged events

    Subclasses are meant to act as namespaces, providing methods for each
    of their variants.
    """

    def __init__(
        self,
        user_msg: str = "",
        log_msg: str = "",
        error: bool = False,
    ) -> None:
        self.error = error
        self.user_msg = user_msg
        self.log_msg = log_msg

    def __str__(self) -> str:
        return f"{self.log_msg}"

    @staticmethod
    def unknown_error() -> "Event":
        """An unknown error occured"""

        return Event(
            user_msg="Unknown error, please contact a server admin",
            log_msg="(ask somebody to) check the logs",
            error=True,
        )

    @staticmethod
    def forbidden(user: User | Member, cmd: Command) -> "Event":
        """The bot tried to do something it is not allowed to"""

        return Event(
            user_msg="Unknown error, please contact a server admin",
            log_msg=f"{user.mention} induced a Forbidden error with command {util.render_command(cmd)}",
            error=True,
        )

    @staticmethod
    def cannot_message_user(user: User | Member, cmd: Command) -> "Event":
        """The bot tried to message a user it wasn't allowed to"""

        return Event(
            user_msg="The bot is not allowed to send messages to you, please check if you have accidentally blocked the bot or if you allow DMs from this server.",
            log_msg=f"DM to {user.mention} was blocked in command {util.render_command(cmd)}",
        )
