from discord import Member, User, TextChannel, Role
from discord.app_commands import Command

from bot.events import Event
from bot import util


class ModerationEvent(Event):
    """Moderation related events"""

    scope = "moderation"

    @classmethod
    def missing_role(
        cls, user: User | Member, cmd: Command, missing_role: Role
    ) -> Event:
        """A user used a command without having a required role"""

        return cls._create_named_event(
            user_msg=f"You are not allowed to use this command",
            user=util.render_user(user),
            cmd=util.render_command(cmd),
            missing_role=util.render_role(missing_role),
        )

    @classmethod
    def missing_permissions(
        cls, user: User | Member, cmd: Command, missing_permissions: list[str]
    ) -> Event:
        """A user used a command without having the required permissions"""

        return cls._create_named_event(
            user_msg=f"You are not allowed to use this command",
            user=util.render_user(user),
            cmd=util.render_command(cmd),
            missing_permissions=missing_permissions,
        )

    @classmethod
    def wrong_channel(
        cls,
        user: User | Member,
        cmd: Command,
        used_in: TextChannel,
        allowed_in: TextChannel,
    ) -> Event:
        """A command was used in the wrong channel"""

        return cls._create_named_event(
            user_msg=f"This command can only be used in {util.render_channel(allowed_in)}",
            user=util.render_user(user),
            cmd=util.render_command(cmd),
            used_in=util.render_channel(used_in),
            allowed_in=util.render_channel(allowed_in),
        )
