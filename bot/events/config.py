from discord import Guild, Role, TextChannel

from bot.events import Event
from bot import util


class ConfigEvent(Event):
    """Configuration related events"""

    @classmethod
    def SyncedCommands(cls, guild: Guild, amount: int) -> Event:
        """Synced slash commands"""

        return cls._create_named_event(
            human=f"Synced {amount} commands to the current guild",
            guild=guild.name,
            amount=amount,
        )

    @classmethod
    def SetAdminRole(cls, guild: Guild, role: Role) -> Event:
        """Set or updated the admin role"""

        return cls._create_named_event(
            human=f"Set the admin role to {util.render_role(role)}",
            guild=guild.name,
            role=util.render_role(role),
        )

    @classmethod
    def MissingConfig(cls, guild: Guild) -> Event:
        """The guild does not have a config yet"""

        return cls._create_named_event(
            human="The bot has not been set up properly yet, please notify a server admin",
            guild=guild.name,
        )

    @classmethod
    def SetVerifiedRole(cls, guild: Guild, role: Role, updated: int) -> Event:
        """Set or updated the verified role and updated verified members' roles"""

        return cls._create_named_event(
            human=f"Set the verified role to {util.render_role(role)}, {updated} members updated",
            guild=guild.name,
            role=util.render_role(role),
            updated=updated,
        )

    @classmethod
    def MissingVerifiedRole(cls, guild: Guild) -> Event:
        """No verified role has been set yet"""

        return cls._create_named_event(
            human="The bot has not been set up properly yet, please notify a server admin",
            guild=guild.name,
        )

    @classmethod
    def SetVerificationChannel(cls, guild: Guild, channel: TextChannel) -> Event:
        """Set or updated the verification channel"""

        return cls._create_named_event(
            human=f"Set the verification channel to {util.render_channel(channel)}",
            guild=guild.name,
            channel=util.render_channel(channel),
        )

    @classmethod
    def MissingVerificationChannel(cls, guild: Guild) -> Event:
        """No verified role has been set yet"""

        return cls._create_named_event(
            human="The bot has not been set up properly yet, please notify a server admin",
            guild=guild.name,
        )

    @classmethod
    def SetLoggingChannel(cls, guild: Guild, channel: TextChannel) -> Event:
        """Set or updated the logging channel"""

        return cls._create_named_event(
            human=f"Set the logging channel to {util.render_channel(channel)}",
            guild=guild.name,
            channel=util.render_channel(channel),
        )
