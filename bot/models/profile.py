from typing import Optional

from discord import Guild
from sqlalchemy import Column, TIMESTAMP, Text, select
from sqlalchemy.engine import Result

from models import Base, Model, session_factory


class PendingProfile(Base, Model):
    __tablename__ = "pending_profile"

    discord_id = Column(Text, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    confirmation_code = Column(Text, nullable=False, unique=True)
    registered_at = Column(TIMESTAMP, nullable=False)

    def __repr__(self) -> str:
        return f"PendingProfile(discord_id={self.discord_id}, email={self.email}, confirmation_code={self.confirmation_code}), registered_at={self.registered_at}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PendingProfile):
            return NotImplemented

        return (
            self.discord_id == other.discord_id
            and self.email == other.email
            and self.confirmation_code == other.confirmation_code
            and self.registered_at == other.registered_at
        )

    @classmethod
    async def find_by_discord_id(cls, discord_id: int) -> Optional["PendingProfile"]:
        """Find a pending profile given its discord_id"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.discord_id == str(discord_id))
            )

            r = result.first()
            if r is None:
                return None

            return r[0]

    @classmethod
    async def find_by_email(cls, email: str) -> Optional["PendingProfile"]:
        """Find a pending profile given its email"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.email == email)
            )

            r = result.first()
            if r is None:
                return None

            return r[0]


class VerifiedProfile(Base, Model):
    __tablename__ = "verified_profile"

    discord_id = Column(Text, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    verified_at = Column(TIMESTAMP, nullable=False)

    def __repr__(self) -> str:
        return f"VerifiedProfile(discord_id={self.discord_id}, email={self.email}, verified_at={self.verified_at}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VerifiedProfile):
            return NotImplemented

        return (
            self.discord_id == other.discord_id
            and self.email == other.email
            and self.confirmation_code == other.confirmation_code
            and self.registered_at == other.registered_at
        )

    @classmethod
    async def find_by_discord_id(cls, discord_id: int) -> Optional["VerifiedProfile"]:
        """Find a verified profile given its discord_id"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.discord_id == str(discord_id))
            )

            r = result.first()
            if r is None:
                return None

            return r[0]

    @classmethod
    async def find_by_email(cls, email: str) -> Optional["VerifiedProfile"]:
        """Find a verified profile given its email"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.email == email)
            )

            r = result.first()
            if r is None:
                return None

            return r[0]

    @classmethod
    async def find_in_guild(cls, guild: Guild) -> list["VerifiedProfile"]:
        """Find all profiles in a specific guild that are verified"""

        async with session_factory() as session:
            result: Result = await session.execute(select(cls))
            profiles: list["VerifiedProfile"] = result.scalars().all()

        profiles = filter(
            lambda p: guild.get_member(p.discord_id) is not None, profiles
        )
        return list(profiles)
