import logging
import os

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query


logger = logging.getLogger("db")


engine = create_async_engine(os.environ["DB_URL"], echo=False)
session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


logger.info("database connected")


class Model:
    @classmethod
    async def create(cls, **kwargs) -> "Model":
        """Create a new row"""

        async with session_factory() as session:
            instance = cls(**kwargs)
            session.add(instance)
            await session.commit()

            return instance

    @classmethod
    async def get_all(cls) -> list["Model"]:
        """Get all rows"""

        async with session_factory() as session:
            result: Query = await session.execute(select(cls))

            return result.scalars().all()

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
