import logging
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("bot")

Base = declarative_base()

engine = create_async_engine(os.environ.get("DB_URL"), echo=False)
logger.info("Database connection established")
session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Model:
    @classmethod
    async def create(cls, **kwargs):
        """Create a new row"""

        async with session_factory() as session:
            session.add(cls(**kwargs))
            await session.commit()

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
