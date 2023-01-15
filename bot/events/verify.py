from discord import User, Member

from bot.events import Event
from bot import util


class VerifyEvent(Event):
    """Verification related events"""

    scope = "verify"

    @classmethod
    def double_verification(cls, user: User | Member) -> Event:
        """A user attempted to verify after already having done so"""

        return cls._create_named_event(
            user_msg="It seems you are trying to verify again despite already having done so in the past\nIf you think this is a mistake please contact a server admin",
            user=util.render_user(user),
        )

    @classmethod
    def code_reset_request(cls, user: User | Member, email: str) -> Event:
        """A user requested a new verification code"""

        return cls._create_named_event(
            user_msg=f"It seems you had already requested a confirmation code before\nThis code has been revoked and a new one has been sent to '{email}'\nPlease use `/verify <code>` now to complete verification",
            user=util.render_user(user),
            email=email,
        )

    @classmethod
    def duplicate_email(cls, user: User | Member) -> Event:
        """A user request a verification code for an email that's already used"""

        return cls._create_named_event(
            user_msg="A different profile with this email already exists\nIf you think this is a mistake please contact a server admin",
            user=util.render_user(user),
        )

    @classmethod
    def code_request(cls, user: User | Member, email: str) -> Event:
        """A user requested a verification code"""

        return cls._create_named_event(
            user_msg=f"A confirmation code has been sent to '{email}'\nPlease use `/verify <code>` now to complete verification",
            user=util.render_user(user),
            email=email,
        )

    @classmethod
    def missing_code(cls, user: User | Member) -> Event:
        """A user attempted to verify without a code"""

        return cls._create_named_event(
            user_msg="It seems you are trying to verify a code without having requested one first\nPlease use `/verify <email>` to request a code",
            user=util.render_user(user),
        )

    @classmethod
    def invalid_code(cls, user: User | Member) -> Event:
        """A user attempted to verify with an invalid code"""

        return cls._create_named_event(
            user_msg="This verification code is incorrect\nIf you would like to request a new code you may do so by using `/verify <email>`",
            user=util.render_user(user),
        )

    @classmethod
    def verified(cls, user: User | Member) -> Event:
        """A user verified"""

        return cls._create_named_event(
            user_msg="You have verified succesfully! Welcome to the server",
            user=util.render_user(user),
        )

    @classmethod
    def malformed_argument(cls, user: User | Member, arg: str) -> Event:
        """A user tried to verify with a malformed argument"""

        return cls._create_named_event(
            user_msg="This doesn't look like a valid UGent email or a valid verification code\nIf you think this is a mistake please contact a server admin",
            user=util.render_user(user),
            arg=arg,
        )


class EmailEvent(Event):
    """Email related events"""

    scope = "verification email"

    @classmethod
    def creating(cls, recipient: str) -> Event:
        """Started creating an email"""

        cls._create_named_event(recipient=recipient)

    @classmethod
    def sent(cls) -> Event:
        """Email sent"""

        cls._create_named_event()
