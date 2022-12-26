from bot.events import Event


class Bot(Event):
    """Events related to the bot itself"""

    @classmethod
    def Ready(cls) -> Event:
        """The bot is ready to accept commands"""

        return cls._create_named_event(human=f"")

    @classmethod
    def ClientClosed(cls) -> Event:
        """The bot's client has been closed"""

        return cls._create_named_event(human=f"")

    @classmethod
    def Exited(cls) -> Event:
        """The bot has exited"""

        return cls._create_named_event(human=f"")

    @classmethod
    def DatabaseConnected(cls) -> Event:
        """The bot has connected to its database"""

        return cls._create_named_event(human=f"")

    @classmethod
    def DatabaseClosed(cls) -> Event:
        """The bot has disconnected from its database"""

        return cls._create_named_event(human=f"")

    @classmethod
    def ExtensionLoaded(cls, extension: str) -> Event:
        """The bot has loaded an extension"""

        return cls._create_named_event(human=f"", extension=extension)

    @classmethod
    def ExtensionUnloaded(cls, extension: str) -> Event:
        """The bot has unloaded an extension"""

        return cls._create_named_event(human=f"", extension=extension)

    @classmethod
    def CogAdded(cls, cog: str) -> Event:
        """The bot has added a cog"""

        return cls._create_named_event(human=f"", cog=cog)

    @classmethod
    def CogRemoved(cls, cog: str) -> Event:
        """The bot has removed a cog"""

        return cls._create_named_event(human=f"", cog=cog)
