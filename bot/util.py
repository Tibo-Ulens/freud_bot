from functools import wraps
import logging
from typing import Coroutine

import discord
from discord import (
    Interaction,
    app_commands,
    User,
    Member,
    Role,
    TextChannel,
    VoiceChannel,
)
from discord.app_commands import Command
from discord.app_commands.errors import MissingRole

from bot.models.course import Course
from bot.models.config import Config


logger = logging.getLogger("bot")


def levenshtein_distance(s1: str, s2: str) -> int:
    """Get the levenshtein distance between two strings to check 'likeness'"""

    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for index2, char2 in enumerate(s2):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(s1):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(
                    1
                    + min((distances[index1], distances[index1 + 1], new_distances[-1]))
                )
        distances = new_distances

    return distances[-1] / max(len(s1), len(s2))


async def course_autocomplete(
    _: Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """
    Order the list of availble courses by 'likeness' to the current argument
    and send them as an autocomplete list
    """

    courses = await Course.get_all_names()
    courses.sort(key=lambda c: levenshtein_distance(c, current))

    return [app_commands.Choice(name=course, value=course) for course in courses]


def enable_guild_logging(func: Coroutine):
    """
    If the wrapped function takes an `Interaction` as an argument, sets a
    custom `__interaction__` attribute on the function that refers to said
    `Interaction`

    This attribute is then extracted in the `GuildAdapter` logging adapter,
    and used by the `DiscordHandler` logging handler to write to the correct
    channel
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Interaction):
                setattr(func, "__interaction__", arg)

        return await func(*args, **kwargs)

    return wrapper


def has_admin_role() -> bool:
    async def predicate(ia: Interaction) -> bool:
        guild_config = await Config.get(ia.guild_id)
        if guild_config is None:
            return False

        admin_role = discord.utils.get(ia.guild.roles, id=guild_config.admin_role)

        if ia.user.get_role(admin_role.id) is None:
            raise MissingRole(admin_role)

        return True

    return app_commands.check(predicate)


def render_user(user: User | Member) -> str:
    """Render a user object as a discord mention"""

    return f"<@{user.id}>"


def render_role(role: Role) -> str:
    """Render a role object as a discord mention"""

    return f"<@&{role.id}>"


def render_channel(channel: TextChannel | VoiceChannel) -> str:
    """Render a channel object as a discord mention"""

    return f"<#{channel.id}>"


def render_command(cmd: Command) -> str:
    group = f"{cmd.parent.name} " if cmd.parent else ""
    return f"/{group}{cmd.name}"
