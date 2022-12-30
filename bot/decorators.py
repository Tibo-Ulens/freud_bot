from functools import wraps
from typing import Coroutine

import discord
from discord import (
    Interaction,
    app_commands,
)
from discord.app_commands.errors import MissingRole
from discord.ext.commands import Context

from bot.models.config import Config


def store_command_context(func: Coroutine) -> Coroutine:
    """
    If the wrapped function takes an `Interaction` as an argument, sets a
    custom `__interaction__` attribute on the function that refers to said
    `Interaction`

    If the wrapped function takes a `Context` as an argument, sets a
    custom `__context__` attribute on the function that refers to said
    `Context`

    This attribute can then be extracted in the `GuildAdapter` logging adapter,
    and used by the `DiscordHandler` logging handler to write to the correct
    channel
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Interaction):
                setattr(func, "__interaction__", arg)
            elif isinstance(arg, Context):
                setattr(func, "__context__", arg)

        return await func(*args, **kwargs)

    return wrapper


def has_admin_role() -> bool:
    async def predicate(ia: Interaction) -> bool:
        # TODO: implement another check/decorator to see if the admin_role
        # config is set or not + add custom error types

        guild_config = await Config.get(ia.guild_id)
        if guild_config is None:
            return False

        admin_role = discord.utils.get(ia.guild.roles, id=guild_config.admin_role)

        if ia.user.get_role(admin_role.id) is None:
            raise MissingRole(admin_role)

        return True

    return app_commands.check(predicate)
