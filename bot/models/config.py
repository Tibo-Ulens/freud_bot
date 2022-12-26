import logging
from typing import Optional
from sqlalchemy import Column, Text
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from bot.models import Base, Model, session_factory


logger = logging.getLogger("models")


class Config(Base, Model):
    __tablename__ = "config"

    guild_id = Column(Text, primary_key=True)
    verified_role = Column(Text, unique=True, nullable=False)
    verification_channel = Column(Text, unique=True, nullable=False)
    admin_role = Column(Text, unique=True, nullable=False)
    logging_channel = Column(Text, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"Config(guild_id={self.guild_id}, verified_role={self.verified_role}, verification_channel={self.verification_channel}, admin_role={self.admin_role}, logging_channel={self.logging_channel})"

    @classmethod
    async def get(cls, id_: int) -> Optional["Config"]:
        """Find a config given its guild ID"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(cls.guild_id == str(id_))
            )

            r = result.first()
            if r is None:
                return None
            else:
                return r[0]

    @classmethod
    async def get_or_create(cls, id_: int) -> "Config":
        """Find a config given its guild ID, or create an empty config if it does not exist"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(cls.guild_id == str(id_))
            )

            r = result.first()
            if r is None:
                logger.info(f"created new config for guild {id_}")
                return await Config.create(guild_id=str(id_), verified_role=None)
            else:
                return r[0]
