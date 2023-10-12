from typing import Optional

from discord import Guild
from sqlalchemy import Column, Text, BigInteger, Integer, select, update
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import Query

from models import Base, Model, session_factory
from models.profile_statistics import ProfileStatistics


class Profile(Base, Model):
    __tablename__ = "profile"

    discord_id = Column(BigInteger, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    confirmation_code = Column(Text, unique=True)
    confession_exposed_count = Column(Integer, FetchedValue(), nullable=False)

    def __repr__(self) -> str:
        return f"Profile(discord_id={self.discord_id}, email={self.email}, confirmation_code={self.confirmation_code})"

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
            result: Query = await session.execute(
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
            result: Query = await session.execute(select(cls).where(cls.email == email))

            r = result.first()
            if r is None:
                return None

            return r[0]

    @classmethod
    async def find_verified_in_guild(cls, guild: Guild) -> list["Profile"]:
        """Find all profiles in a specific guild that are verified"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(
                    cls.confirmation_code.is_(None), cls.email.is_not(None)
                )
            )

            profiles: list["Profile"] = result.scalars().all()

        profiles = filter(
            lambda p: guild.get_member(p.discord_id) is not None, profiles
        )
        return list(profiles)

    @classmethod
    async def increment_exposed_count(cls, discord_id: int):
        """Increment the confession exposed count for a profile given their ID"""

        async with session_factory() as session:
            stmt = (
                update(cls)
                .where(cls.discord_id == discord_id)
                .values(confession_exposed_count=cls.confession_exposed_count + 1)
                .returning(cls.confession_exposed_count)
            )

            await session.execute(stmt)
            await session.commit()

        return

    @classmethod
    async def get_exposed_top_10(cls) -> list["Profile"]:
        """Get a top 10 of the most exposed users"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls)
                .order_by(cls.confession_exposed_count.desc(), cls.email.asc())
                .limit(10)
            )

        return result.scalars().all()

    async def get_freudpoint_rank(self) -> int:
        """Get a profiles freudpoint score rank"""

        async with session_factory() as session:
            query: Query = await session.execute(
                select(Profile)
                .join(ProfileStatistics)
                .order_by(ProfileStatistics.freudpoints.desc(), Profile.email.desc())
            )

        profiles: list["Profile"] = query.scalars().all()

        return profiles.index(self)
