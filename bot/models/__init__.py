from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import bot

engine = bot.instance.db
session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


class Model:
    @classmethod
    async def create(cls, **kwargs) -> "Model":
        """Create a new row"""

        async with session_factory() as session:
            instance = cls(**kwargs)
            session.add(instance)
            await session.commit()

            return instance

    async def save(self):
        """Save an updated row"""

        async with session_factory() as session:
            session.add(self)
            await session.commit()

    async def delete(self):
        """Delete a row"""

        async with session_factory() as session:
            await session.delete(self)
            await session.commit()
