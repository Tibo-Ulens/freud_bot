import logging
from typing import Optional

from sqlalchemy import Column, BigInteger, Integer, Text
from sqlalchemy.schema import FetchedValue
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from discord import Guild

from models import Base, Model, session_factory


logger = logging.getLogger("models")


class Config(Base, Model):
    __tablename__ = "config"

    guild_id = Column(BigInteger, primary_key=True)
    verified_role = Column(BigInteger, unique=True, nullable=True)
    admin_role = Column(BigInteger, unique=True, nullable=True)
    logging_channel = Column(BigInteger, unique=True, nullable=True)
    confession_approval_channel = Column(BigInteger, unique=True, nullable=True)
    confession_channel = Column(BigInteger, unique=True, nullable=True)
    pin_reaction_threshold = Column(Integer, FetchedValue(), nullable=False)
    verify_email_message = Column(Text, FetchedValue(), nullable=False)
    new_email_message = Column(Text, FetchedValue(), nullable=False)
    invalid_email_message = Column(Text, FetchedValue(), nullable=False)
    duplicate_email_message = Column(Text, FetchedValue(), nullable=False)
    verify_code_message = Column(Text, FetchedValue(), nullable=False)
    invalid_code_message = Column(Text, FetchedValue(), nullable=False)
    already_verified_message = Column(Text, FetchedValue(), nullable=False)
    welcome_message = Column(Text, FetchedValue(), nullable=False)

    def __repr__(self) -> str:
        return f"Config(guild_id={self.guild_id}, verified_role={self.verified_role}, admin_role={self.admin_role}, logging_channel={self.logging_channel}, confession_approval_channel={self.confession_approval_channel}, confession_channel={self.confession_channel})"

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
                return await Config.create(guild_id=guild.id)

            return r[0]

    def update(self, changes: dict[str, any]) -> "Config":
        """Update a config given a dict of changes"""

        for col in self.cols():
            if col.name in changes:
                if str(col.type) == "TEXT":
                    setattr(self, col.name, str(changes[col.name]))
                else:
                    setattr(self, col.name, int(changes[col.name]))

        return self
