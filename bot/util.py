from discord import Interaction, app_commands

from bot.models.course import Course


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


def check_has_manage_guild(ia: Interaction) -> bool:
    """Check if a user has the "manage guild" permission"""

    return ia.user.guild_permissions.manage_guild
