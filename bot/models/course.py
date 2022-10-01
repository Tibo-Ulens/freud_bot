import asyncio
from typing import Optional
from sqlalchemy import Column, Text
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from bot.models import Base, Model, session_factory
from bot.models.enrollment import Enrollment


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
    async def find_by_code(cls, code: str) -> Optional["Course"]:
        """Find a course given its code"""

        async with session_factory() as session:
            result: Query = await session.execute(select(cls).where(cls.code == code))

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
        """Delete a course and its enrollments"""

        async with session_factory() as session:
            enrollments = await Enrollment.find_for_course(self.code)
            await asyncio.gather(*[session.delete(e) for e in enrollments])

            await session.delete(self)
            await session.commit()
