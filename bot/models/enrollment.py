from typing import Optional
from sqlalchemy import Column, Text
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from bot.models import Base, Model, session_factory


class Enrollment(Base, Model):
    __tablename__ = "enrollment"

    profile_id = Column(Text, primary_key=True)
    course_id = Column(Text, primary_key=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}> profile_id: {self.profile_id} course_id: {self.course_id}"

    @classmethod
    async def find(cls, profile_id: str, course_id: str) -> Optional["Enrollment"]:
        """Find a specific enrollment"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls)
                .where(cls.profile_id == profile_id)
                .where(cls.course_id == course_id)
            )

            r = result.first()
            if r is None:
                return None
            else:
                return r[0]

    @classmethod
    async def find_for_profile(cls, profile_id: str) -> list["Enrollment"]:
        """Find all enrollments for a given profile"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(cls.profile_id == profile_id)
            )

            return result.scalars().all()

    @classmethod
    async def find_for_course(cls, course_id: str) -> list["Enrollment"]:
        """Find all enrollments for a given course"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(cls.course_id == course_id)
            )

            return result.scalars().all()
