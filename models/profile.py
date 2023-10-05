from typing import Optional

from discord import Guild
from sqlalchemy import Column, Text, BigInteger, select, Integer
from sqlalchemy.orm import Query, validates

from models import Base, Model, session_factory


class Profile(Base, Model):
    __tablename__ = "profile"

    discord_id = Column(BigInteger, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    confirmation_code = Column(Text, unique=True)
    freudpoints = Column(Integer, nullable=False)
    spendable_freudpoints = Column(Integer, nullable=False)
    max_spendable_freudpoints = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"Profile(discord_id={self.discord_id}, email={self.email}, confirmation_code={self.confirmation_code})"

    @validates("freudpoints")
    def validate_fp_positive(self, key, value):
        if value < 0:
            raise ValueError(f"FreudPoints must be at least 0")

        return value

    @validates("spendable_freudpoints")
    def validate_spendable_fp_positive(self, key, value):
        if value < 0:
            raise ValueError(f"spendable FreudPoints must be at least 0")

        return value

    @validates("max_spendable_freudpoints")
    def validate_max_spendable_fp_positive(self, key, value):
        if value < 0:
            raise ValueError(f"maximum spendable FreudPoints must be at least 0")

        return value

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
