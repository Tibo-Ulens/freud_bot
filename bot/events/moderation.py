from discord import Member, User

from bot.events import Event


class Moderation(Event):
    """Moderaton related events"""

    @classmethod
    def PermissionViolation(cls, user: Member | User) -> Event:
        """A user used a command without proper permissions"""

        user_str = f"[{user.id}] {user.nick or user.name}"

        return cls._create_named_event(user=user_str)
