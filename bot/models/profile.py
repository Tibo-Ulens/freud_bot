from typing import Optional

from sqlalchemy import Column, Text, BigInteger
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from bot.models import Base, Model, session_factory


class Profile(Base, Model):
    __tablename__ = "profile"

    discord_id = Column(BigInteger, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    confirmation_code = Column(Text, unique=True)

    def __repr__(self) -> str:
        return f"Profile(discord_id={self.discord_id}, email={self.email}, confirmation_code={self.confirmation_code})"

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
            else:
                return r[0]

    @classmethod
    async def find_by_email(cls, email: str) -> Optional["Profile"]:
        """Find a profile given its email"""

        async with session_factory() as session:
            result: Query = await session.execute(select(cls).where(cls.email == email))

            r = result.first()
            if r is None:
                return None
            else:
                return r[0]
