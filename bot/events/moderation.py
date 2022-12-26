from discord import Member, User

from bot.events import Event
from bot import util


class Moderation(Event):
    """Moderation related events"""

    @classmethod
    def PermissionViolation(cls, user: Member | User) -> Event:
        """A user used a command without proper permissions"""

        return cls._create_named_event(user=util.render_user(user))
