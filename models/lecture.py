from sqlalchemy import Column, Text, Integer, select
from sqlalchemy.engine import Result

from models import Base, Model, session_factory


class Lecture(Base, Model):
    __tablename__ = "lecture"

    id = Column(Integer, primary_key=True)
    course_code = Column(Text, nullable=False)
    course_name = Column(Text, nullable=False)
    start_date = Column(Text, nullable=False)
    start_time = Column(Text, nullable=False)
    end_date = Column(Text, nullable=False)
    end_time = Column(Text, nullable=False)
    lecture_type = Column(Text, nullable=False)
    lecturer = Column(Text, nullable=False)
    classroom = Column(Text, nullable=False)
    building = Column(Text, nullable=False)
    campus = Column(Text, nullable=False)

    @classmethod
    async def from_csv_entry(cls, entry: dict[str, str]) -> "Lecture":
        """Build and store a lecture object from a TimeEdit CSV entry"""

        location_parts = entry["Lokaal,Gebouw,Campus"].split(".")
        [classroom, building, campus] = (
            location_parts if len(location_parts) == 3 else ["", "", ""]
        )

        # start_datetime = datetime.strptime(
        #     f"{entry['Start datum']} {entry['Begin tijd']}", "%d-%m-%Y %H:%M"
        # )
        # end_datetime = datetime.strptime(
        #     f"{entry['Eind datum']} {entry['Eind tijd']}", "%d-%m-%Y %H:%M"
        # )

        return await cls.create(
            course_code=entry["Cursuscode,Naam"].split(".")[0].strip(),
            course_name=entry["Cursuscode,Naam"].split(".")[1].strip(),
            start_date=entry["Start datum"],
            start_time=entry["Starttijd"],
            end_date=entry["Eind datum"],
            end_time=entry["Eindtijd"],
            lecture_type=entry["Aard"],
            lecturer=entry["Lesgever"],
            classroom=classroom.strip(),
            building=building.strip(),
            campus=campus.strip(),
        )

    @classmethod
    async def find_for_course(cls, course_code: str) -> list["Lecture"]:
        """Find all lectures for a given course"""

        async with session_factory() as session:
            result: Result = await session.execute(
                select(cls).where(cls.course_code == course_code)
            )

            return result.scalars().all()
