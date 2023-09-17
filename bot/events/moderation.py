from discord import Member, User, TextChannel, Role
from discord.app_commands import Command

from bot.events import Event
from bot import util


class ModerationEvent(Event):
    """Moderation related events"""

    scope = "moderation"

    @staticmethod
    def missing_role(user: User | Member, cmd: Command, missing_role: Role) -> Event:
        """A user used a command without having a required role"""

        return Event(
            user_msg="You are not allowed to use this command",
            log_msg=f"user {util.render_user(user)} attempted to use command {util.render_command(cmd)} without having role {util.render_role(missing_role)}",
        )

    @staticmethod
    def missing_permissions(
        user: User | Member, cmd: Command, missing_permissions: list[str]
    ) -> Event:
        """A user used a command without having the required permissions"""

        return Event(
            user_msg="You are not allowed to use this command",
            log_msg=f"user {util.render_user(user)} attempted to use command {util.render_command(cmd)} without having permissions {','.join(missing_permissions)}",
        )

    @staticmethod
    def wrong_channel(
        user: User | Member,
        cmd: Command,
        used_in: TextChannel,
        allowed_in: TextChannel,
    ) -> Event:
        """A command was used in the wrong channel"""

        return Event(
            user_msg=f"This command can only be used in {util.render_channel(allowed_in)}",
            log_msg=f"user {util.render_user(user)} attempted to use command {util.render_command(cmd)} in channel {util.render_channel(used_in)}, but it is only allowed in {util.render_channel(allowed_in)}",
        )
