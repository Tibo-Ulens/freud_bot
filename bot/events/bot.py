from discord import Guild

from bot.events import Event


class BotEvent(Event):
    """Events related to the bot itself"""

    scope = "bot"

    @classmethod
    def bot_ready(cls) -> Event:
        """The bot is ready to accept commands"""

        return cls._create_named_event()

    @classmethod
    def synced_commands(cls, guild: Guild, amount: int) -> Event:
        """Synced slash commands"""

        return cls._create_named_event(
            user_msg=f"Synced {amount} commands to the current guild",
            guild=guild.name,
            amount=amount,
        )

    @classmethod
    def guild_available(cls, guild: Guild) -> Event:
        """a guild has become available"""

        return cls._create_named_event(guild=guild.name)

    @classmethod
    def client_closed(cls) -> Event:
        """The bot's client has been closed"""

        return cls._create_named_event()

    @classmethod
    def bot_exited(cls) -> Event:
        """The bot has exited"""

        return cls._create_named_event()

    @classmethod
    def database_connected(cls) -> Event:
        """The bot has connected to its database"""

        return cls._create_named_event()

    @classmethod
    def database_closed(cls) -> Event:
        """The bot has disconnected from its database"""

        return cls._create_named_event()

    @classmethod
    def extension_loaded(cls, extension: str) -> Event:
        """The bot has loaded an extension"""

        return cls._create_named_event(extension=extension)

    @classmethod
    def extension_unloaded(cls, extension: str) -> Event:
        """The bot has unloaded an extension"""

        return cls._create_named_event(extension=extension)

    @classmethod
    def cog_added(cls, cog: str) -> Event:
        """The bot has added a cog"""

        return cls._create_named_event(cog=cog)

    @classmethod
    def cog_removed(cls, cog: str) -> Event:
        """The bot has removed a cog"""

        return cls._create_named_event(cog=cog)
