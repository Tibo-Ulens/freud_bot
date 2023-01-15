import logging
from typing import Optional
from sqlalchemy import Column, BigInteger
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from discord import Guild

from bot.models import Base, Model, session_factory
from bot.events.config import ConfigEvent


logger = logging.getLogger("models")


class Config(Base, Model):
    __tablename__ = "config"

    guild_id = Column(BigInteger, primary_key=True)
    verified_role = Column(BigInteger, unique=True, nullable=False)
    verification_channel = Column(BigInteger, unique=True, nullable=False)
    admin_role = Column(BigInteger, unique=True, nullable=False)
    logging_channel = Column(BigInteger, unique=True, nullable=False)
    confession_approval_channel = Column(BigInteger, unique=True, nullable=False)
    confession_channel = Column(BigInteger, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"Config(guild_id={self.guild_id}, verified_role={self.verified_role}, verification_channel={self.verification_channel}, admin_role={self.admin_role}, logging_channel={self.logging_channel}, confession_approval_channel={self.confession_approval_channel}, confession_channel={self.confession_channel})"

    @classmethod
    async def get(cls, guild_id: int) -> Optional["Config"]:
        """Find a config given its guild ID"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(cls.guild_id == guild_id)
            )

            r = result.first()
            if r is None:
                return None
            else:
                return r[0]

    @classmethod
    async def get_or_create(cls, guild: Guild) -> "Config":
        """Find a config given its guild ID, or create an empty config if it does not exist"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(cls.guild_id == guild.id)
            )

            r = result.first()
            if r is None:
                logger.info(ConfigEvent.new_config_created(guild))
                return await Config.create(guild_id=guild.id, verified_role=None)
            else:
                return r[0]
