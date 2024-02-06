from typing import Optional

from discord import Guild
from sqlalchemy import Column, Text, BigInteger, select
from sqlalchemy.engine import Result
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.sql import text

from models import Base, Model, session_factory
from models.profile_statistics import ProfileStatistics


class MutableList(Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.changed()

    def append(self, value):
        list.append(self, value)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()


class Profile(Base, Model):
    __tablename__ = "profile"

    discord_id = Column(BigInteger, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    confirmation_code = Column(Text, unique=True)
    crushes = Column(
        MutableList.as_mutable(ARRAY(BigInteger)), FetchedValue(), nullable=False
    )

    def __repr__(self) -> str:
        return f"Profile(discord_id={self.discord_id}, email={self.email}, confirmation_code={self.confirmation_code}), crushes={self.crushes}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Profile):
            return NotImplemented

        return (
            self.discord_id == other.discord_id
            and self.email == other.email
            and self.confirmation_code == other.confirmation_code
        )

    @classmethod
    async def find_by_discord_id(cls, discord_id: int) -> Optional["Profile"]:
        """Find a profile given its discord_id"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.discord_id == discord_id)
            )

            r = result.first()
            if r is None:
                return None

            return r[0]

    @classmethod
    async def find_by_email(cls, email: str) -> Optional["Profile"]:
        """Find a profile given its email"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.email == email)
            )

            r = result.first()
            if r is None:
                return None

            return r[0]

    @classmethod
    async def find_verified_in_guild(cls, guild: Guild) -> list["Profile"]:
        """Find all profiles in a specific guild that are verified"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(
                    cls.confirmation_code.is_(None), cls.email.is_not(None)
                )
            )

            profiles: list["Profile"] = result.scalars().all()

        profiles = filter(
            lambda p: guild.get_member(p.discord_id) is not None, profiles
        )
        return list(profiles)

    async def get_freudpoint_rank(self, guild_id: int) -> int:
        """Get a profiles FreudPoint score rank in a given guild"""

        async with session_factory() as session:
            query: Result = await session.execute(
                select(Profile)
                .join(ProfileStatistics)
                .where(ProfileStatistics.config_guild_id == guild_id)
                .order_by(ProfileStatistics.freudpoints.desc())
            )

        profiles: list["Profile"] = query.scalars().all()

        return profiles.index(self)

    def is_verified(self) -> bool:
        """Check if a profile is verified"""

        return self.email is not None and self.confirmation_code is None
