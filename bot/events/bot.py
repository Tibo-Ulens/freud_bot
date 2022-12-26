from bot.events import Event


class Bot(Event):
    """Events related to the bot itself"""

    @classmethod
    def Ready(cls) -> Event:
        """The bot is ready to accept commands"""

        return cls._create_named_event(human=f"")
