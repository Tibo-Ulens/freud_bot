import discord
from discord import (
    Interaction,
    app_commands,
)
from discord.app_commands.errors import MissingRole

from models.config import Config

from bot.exceptions import MissingConfig, MissingConfigOption, WrongChannel


def check_user_has_admin_role() -> bool:
    """
    Check if the user calling the command has the corresponding admin role in
    their guild
    """

    async def predicate(ia: Interaction) -> bool:
        guild_config = await Config.get(ia.guild_id)
        if guild_config is None:
            raise MissingConfig(ia.guild)

        if guild_config.admin_role is None:
            raise MissingConfigOption(ia.guild, "admin_role")

        admin_role = discord.utils.get(ia.guild.roles, id=guild_config.admin_role)

        if ia.user.get_role(admin_role.id) is None:
            raise MissingRole(admin_role)

        return True

    return app_commands.check(predicate)


def check_user_is_verified() -> bool:
    """Check if the user calling the command is verified or not"""

    async def predicate(ia: Interaction) -> bool:
        guild_config = await Config.get(ia.guild_id)
        if guild_config is None:
            raise MissingConfig(ia.guild)

        if guild_config.verified_role is None:
            raise MissingConfigOption(ia.guild, "verified_role")

        verified_role = discord.utils.get(ia.guild.roles, id=guild_config.verified_role)

        if ia.user.get_role(verified_role.id) is None:
            raise MissingRole(verified_role)

        return True

    return app_commands.check(predicate)


def check_has_config_option(option: str) -> bool:
    """
    Check if the guild this command is called in has a given config option set
    or not
    """

    async def predicate(ia: Interaction) -> bool:
        guild_config = await Config.get(ia.guild_id)
        if guild_config is None:
            raise MissingConfig(ia.guild)

        if getattr(guild_config, option) is None:
            raise MissingConfigOption(ia.guild, option)

        return True

    return app_commands.check(predicate)


def only_in_channel(channel_option: str) -> bool:
    """
    Ensure the command can only be used in the specified channel

    The argument must be the name of a config option
    """

    async def predicate(ia: Interaction) -> bool:
        guild_config = await Config.get(ia.guild_id)
        if guild_config is None:
            raise MissingConfig(ia.guild)

        if getattr(guild_config, channel_option) is None:
            raise MissingConfigOption(ia.guild, channel_option)

        allowed_channel = discord.utils.get(
            ia.guild.text_channels, id=getattr(guild_config, channel_option)
        )

        if ia.channel_id != allowed_channel.id:
            raise WrongChannel(
                ia.guild, ia.user, ia.command, ia.channel, allowed_channel
            )

        return True

    return app_commands.check(predicate)
