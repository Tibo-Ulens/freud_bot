from typing import Optional
from sqlalchemy import Column, Text
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from bot.models import Base, Model, session_factory


class Course(Base, Model):
    __tablename__ = "course"

    code = Column(Text, primary_key=True)
    name = Column(Text, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}> code: {self.code} name: {self.name}"

    @classmethod
    async def find_by_name(cls, name: str) -> Optional["Course"]:
        """Find a course given its name"""

        async with session_factory() as session:
            result: Query = await session.execute(select(cls).where(cls.name == name))

            r = result.first()
            if r is None:
                return None
            else:
                return r[0]

    @classmethod
    async def get_all(cls) -> list[str]:
        """Get the name of all available courses"""

        async with session_factory() as session:
            result: Query = await session.execute(select(cls))

            return result.scalars().all()

    async def delete(self):
        """Delete a course"""

        async with session_factory() as session:
            await session.delete(self)
            await session.commit()
