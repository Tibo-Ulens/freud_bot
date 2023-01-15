from discord import Guild, Role, TextChannel

from bot.events import Event
from bot import util


class ConfigEvent(Event):
    """Configuration related events"""

    scope = "config"

    @classmethod
    def set_admin_role(cls, guild: Guild, role: Role) -> Event:
        """Set or updated the admin role"""

        return cls._create_named_event(
            user_msg=f"Set the admin role to {util.render_role(role)}",
            guild=guild.name,
            role=util.render_role(role),
        )

    @classmethod
    def new_config_created(cls, guild: Guild) -> Event:
        """A new config was created"""

        return cls._create_named_event(guild=guild.name)

    @classmethod
    def missing_config(cls, guild: Guild) -> Event:
        """The guild does not have a config yet"""

        return cls._create_named_event(
            user_msg="The bot has not been set up properly yet, please notify a server admin",
            error=True,
            guild=guild.name,
        )

    @classmethod
    def missing_config_option(cls, guild: Guild, option: str) -> Event:
        """The guild is missing a config option"""

        return cls._create_named_event(
            user_msg="The bot has not been set up properly yet, please notify a server admin",
            error=True,
            guild=guild.name,
            option=option,
        )

    @classmethod
    def set_verified_role(cls, guild: Guild, role: Role, updated: int) -> Event:
        """Set or updated the verified role and updated verified members' roles"""

        return cls._create_named_event(
            user_msg=f"Set the verified role to {util.render_role(role)}, {updated} members updated",
            guild=guild.name,
            role=util.render_role(role),
            updated=updated,
        )

    @classmethod
    def missing_verified_role(cls, guild: Guild) -> Event:
        """No verified role has been set yet"""

        return cls._create_named_event(
            user_msg="The bot has not been set up properly yet, please notify a server admin",
            guild=guild.name,
        )

    @classmethod
    def set_verification_channel(cls, guild: Guild, channel: TextChannel) -> Event:
        """Set or updated the verification channel"""

        return cls._create_named_event(
            user_msg=f"Set the verification channel to {util.render_channel(channel)}",
            guild=guild.name,
            channel=util.render_channel(channel),
        )

    @classmethod
    def missing_verification_channel(cls, guild: Guild) -> Event:
        """No verified role has been set yet"""

        return cls._create_named_event(
            user_msg="The bot has not been set up properly yet, please notify a server admin",
            guild=guild.name,
        )

    @classmethod
    def set_logging_channel(cls, guild: Guild, channel: TextChannel) -> Event:
        """Set or updated the logging channel"""

        return cls._create_named_event(
            user_msg=f"Set the logging channel to {util.render_channel(channel)}",
            guild=guild.name,
            channel=util.render_channel(channel),
        )
