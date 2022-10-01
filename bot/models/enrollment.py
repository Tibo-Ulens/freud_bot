from sqlalchemy import Column, Text
from sqlalchemy.future import select
from sqlalchemy.orm import Query

from bot.models import Base, Model, session_factory
from bot.models.profile import Profile


class Enrollment(Base, Model):
    __tablename__ = "enrollment"

    profile_id = Column(Text, primary_key=True)
    course_id = Column(Text, primary_key=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}> profile_id: {self.profile_id} course_id: {self.course_id}"

    @classmethod
    async def find_for_profile(cls, profile_id: str) -> list["Enrollment"]:
        """Find all enrollments for a given profile"""

        async with session_factory() as session:
            result: Query = await session.execute(
                select(cls).where(cls.profile_id == profile_id)
            )

            return result.scalars().all()
