from discord import Guild
from discord.app_commands import CheckFailure


class MissingConfig(CheckFailure):
    """No configuration was found for a given guild"""

    def __init__(self, guild: Guild) -> None:
        self.guild = guild
        self.message = f"missing configuration for guild {guild.name}"

        super().__init__(self.message)


class MissingConfigOption(CheckFailure):
    """Configuration option missing/not set for a given guild"""

    def __init__(self, guild: Guild, option: str) -> None:
        self.guild = guild
        self.option = option

        self.message = f"missing configuration option '{option}' for guild {guild.name}"

        super().__init__(self.message)
