from discord import Guild, Role, TextChannel

from bot.events import Event
from bot import util


class Config(Event):
    """Configuration related events"""

    @classmethod
    def SyncedCommands(cls, guild: Guild, amount: int) -> Event:
        """Synced slash commands"""

        return cls._create_named_event(guild=guild.name, amount=amount)

    @classmethod
    def SetVerifiedRole(cls, guild: Guild, role: Role) -> Event:
        """Set or updated the verified role"""

        return cls._create_named_event(guild=guild.name, role=util.render_role(role))

    @classmethod
    def SetVerificationChannel(cls, guild: Guild, channel: TextChannel) -> Event:
        """Set or updated the verification channel"""

        return cls._create_named_event(
            guild=guild.name, channel=util.render_channel(channel)
        )

    @classmethod
    def SetAdminRole(cls, guild: Guild, role: Role) -> Event:
        """Set or updated the admin role"""

        return cls._create_named_event(guild=guild.name, role=util.render_role(role))
