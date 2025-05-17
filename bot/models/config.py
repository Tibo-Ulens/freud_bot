import logging
from typing import Optional

from sqlalchemy import Column, Integer, Text, select
from sqlalchemy.engine import Result
from sqlalchemy.schema import FetchedValue

from discord import Guild

from models import Base, Model, session_factory


logger = logging.getLogger("models")


class Config(Base, Model):
    __tablename__ = "config"

    guild_id = Column(Text, primary_key=True)

    verified_role = Column(Text, unique=True, nullable=True)
    admin_role = Column(Text, unique=True, nullable=True)

    logging_channel = Column(Text, unique=True, nullable=True)
    verification_logging_channel = Column(Text, unique=True, nullable=True)

    confession_approval_channel = Column(Text, unique=True, nullable=True)
    confession_channel = Column(Text, unique=True, nullable=True)

    pin_reaction_threshold = Column(Integer, FetchedValue(), nullable=False)

    request_verification_message = Column(Text, FetchedValue(), nullable=False)

    @classmethod
    async def get(cls, guild_id: int) -> Optional["Config"]:
        """Find a config given its guild ID"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.guild_id == str(guild_id))
            )

            r = result.first()
            if r is None:
                return None

            return r[0]

    @classmethod
    async def get_or_create(cls, guild: Guild) -> "Config":
        """Find a config given its guild ID, or create an empty config if it does not exist"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.guild_id == str(guild.id))
            )

            r = result.first()
            if r is None:
                return await Config.create(guild_id=str(guild.id))

            return r[0]
