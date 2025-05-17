from discord import Guild, User, TextChannel
from discord.app_commands import CheckFailure, Command

from bot import util


class MissingConfig(CheckFailure):
    """No configuration was found for a given guild"""

    def __init__(self, guild: Guild) -> None:
        self.guild = guild
        self.message = f"missing configuration for guild {util.render_guild(guild)}"

        super().__init__(self.message)


class MissingConfigOption(CheckFailure):
    """Configuration option missing/not set for a given guild"""

    def __init__(self, guild: Guild, option: str) -> None:
        self.guild = guild
        self.option = option

        self.message = f"missing configuration option '{option}' for guild {util.render_guild(guild)}"

        super().__init__(self.message)


class WrongChannel(CheckFailure):
    """Command was used in the wrong channel"""

    def __init__(
        self,
        guild: Guild,
        user: User,
        cmd: Command,
        used_channel: TextChannel,
        allowed_channel: TextChannel,
    ) -> None:
        self.guild = guild
        self.cmd = cmd
        self.user = user
        self.used_channel = used_channel
        self.allowed_channel = allowed_channel

        self.message = f"user {util.render_user(user)} used command {util.render_command(cmd)} in {util.render_channel(used_channel)}"

        super().__init__(self.message)
