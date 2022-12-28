from typing import Optional
from sqlalchemy import Column, Text
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from bot.models import Base, Model, session_factory


class Enrollment(Base, Model):
    __tablename__ = "enrollment"

    profile_discord_id = Column(Text, primary_key=True)
    course_code = Column(Text, primary_key=True)

    def __repr__(self) -> str:
        return f"Enrollment(profile_discord_id={self.profile_discord_id}, course_code={self.course_code})"

    @classmethod
    async def find(
        cls, profile_discord_id: str, course_code: str
    ) -> Optional["Enrollment"]:
        """Find a specific enrollment"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls)
                .where(cls.profile_discord_id == profile_discord_id)
                .where(cls.course_code == course_code)
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
                select(cls).where(cls.profile_discord_id == profile_id)
            )

            return result.scalars().all()

    @classmethod
    async def find_for_course(cls, course_code: str) -> list["Enrollment"]:
        """Find all enrollments for a given course"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(cls.course_code == course_code)
            )

            return result.scalars().all()
