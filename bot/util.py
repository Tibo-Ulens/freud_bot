from discord import Interaction


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


def check_has_manage_guild(ia: Interaction) -> bool:
    """Check if a user has the "manage guild" permission"""

    return ia.user.guild_permissions.manage_guild
