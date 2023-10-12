from typing import Optional
from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey,
    select,
    update,
    Integer,
    func,
)
from sqlalchemy.engine import Result
from sqlalchemy.orm import validates, relationship
from sqlalchemy.schema import FetchedValue

from models import Base, Model, session_factory
from models.config import Config


class ProfileStatistics(Base, Model):
    __tablename__ = "profile_statistics"

    profile_discord_id = Column(
        BigInteger, ForeignKey("profile.discord_id"), primary_key=True
    )
    config_guild_id = Column(
        BigInteger, ForeignKey("config.guild_id"), primary_key=True
    )

    freudpoints = Column(Integer, FetchedValue(), nullable=False)
    spendable_freudpoints = Column(Integer, FetchedValue(), nullable=False)
    confession_exposed_count = Column(Integer, FetchedValue(), nullable=False)

    profile = relationship("Profile", foreign_keys=[profile_discord_id])
    config = relationship("Config", foreign_keys=[config_guild_id])

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

    @classmethod
    async def get(cls, discord_id: int, guild_id: int) -> Optional["ProfileStatistics"]:
        """Find statistics the profile and guild id"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(
                    cls.profile_discord_id == discord_id,
                    cls.config_guild_id == guild_id,
                )
            )

            r = result.first()
            if r is None:
                return None

            return r[0]

    @classmethod
    async def increment_spendable_freudpoints(cls):
        """Increment the spendable freudpoints for each profile by 1 up to the max"""

        async with session_factory() as session:
            max_spendable_subquery = (
                select(Config.max_spendable_freudpoints)
                .where(Config.guild_id == cls.config_guild_id)
                .limit(1)
                .scalar_subquery()
            )

            await session.execute(
                update(cls).values(
                    spendable_freudpoints=func.least(
                        cls.spendable_freudpoints + 1, max_spendable_subquery
                    )
                )
            )

            await session.commit()

    @classmethod
    async def get_freudpoint_top_10(cls, guild_id: int) -> list["ProfileStatistics"]:
        """Get a top 10 of the members in the given guild with the most freudpoints"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls)
                .where(cls.config_guild_id == guild_id)
                .order_by(cls.freudpoints.desc())
                .limit(10)
            )

        return result.scalars().all()

    @classmethod
    async def increment_exposed_count(cls, discord_id: int, guild_id: int):
        """Increment the confession exposed count for a profile in a given server"""

        async with session_factory() as session:
            stmt = (
                update(cls)
                .where(
                    cls.profile_discord_id == discord_id,
                    cls.config_guild_id == guild_id,
                )
                .values(confession_exposed_count=cls.confession_exposed_count + 1)
                .returning(cls.confession_exposed_count)
            )

            await session.execute(stmt)
            await session.commit()

        return

    @classmethod
    async def get_exposed_top_10(cls, guild_id: int) -> list["ProfileStatistics"]:
        """Get a top 10 of the most exposed users for the given guild"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls)
                .where(cls.config_guild_id == guild_id)
                .order_by(cls.confession_exposed_count.desc())
                .limit(10)
            )

        return result.scalars().all()
