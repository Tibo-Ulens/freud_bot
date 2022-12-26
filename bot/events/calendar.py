from discord import User, Member

from bot.events import Event
from bot.models.course import Course
from bot import util


class Course(Event):
    """Events related to courses"""

    @classmethod
    def Added(cls, course: Course) -> Event:
        """Added a course"""

        return cls._create_named_event(human=f"Added course {course}", course=course)

    @classmethod
    def Removed(cls, course: Course) -> Event:
        """Removed a course"""

        return cls._create_named_event(human=f"Removed course {course}", course=course)

    @classmethod
    def Enrolled(cls, user: User | Member, course: Course) -> Event:
        """A user enrolled in a course"""

        return cls._create_named_event(
            human=f"You have enrolled in the course {course}",
            user=util.render_user(user),
            course=course,
        )

    @classmethod
    def Dropped(cls, user: User | Member, course: Course) -> Event:
        """A user dropped a course"""

        return cls._create_named_event(
            human=f"You have dropped the course {course}",
            user=util.render_user(user),
            course=course,
        )


class LectureInfo(Event):
    """Events emitted when handling lecture info"""

    @classmethod
    def DeletingOldInfo(cls, course: Course) -> Event:
        """Started deleting old lecture info"""

        return cls._create_named_event(
            human=f"Deleting old lecture info for course {course}", course=course
        )

    @classmethod
    def Refreshed(cls, course: Course) -> Event:
        """Refreshed lecture info"""

        return cls._create_named_event(
            human=f"Refreshed lecture info for course {course}", course=course
        )

    @classmethod
    def SearchingInfo(cls, course: Course) -> Event:
        """Started searching for lecture info"""

        return cls._create_named_event(
            human=f"Searching lecture info for course {course} (this may take a while)",
            course=course,
        )

    @classmethod
    def DownloadingInfo(cls, course: Course) -> Event:
        """Started downloading lecture info"""

        return cls._create_named_event(
            human=f"Downloading lecture info for course {course}", course=course
        )

    @classmethod
    def StoringInfo(cls, course: Course) -> Event:
        """Started storing lecture info"""

        return cls._create_named_event(
            human=f"Storing lecture info for course {course}", course=course
        )


class TimeEdit(Event):
    """Events emitted while scraping TimeEdit"""

    @classmethod
    def CourseSearch(cls, period: int, course: Course) -> Event:
        """A course was searched on TimeEdit"""

        return cls._create_named_event(period=period, course=course)

    @classmethod
    def CourseAdded(cls, period: int, course: Course) -> Event:
        """A course was added on TimeEdit"""

        return cls._create_named_event(period=period, course=course)

    @classmethod
    def CourseNotfound(cls, period: int, course: Course) -> Event:
        """A course was not found on TimeEdit"""

        return cls._create_named_event(period=period, course=course)

    @classmethod
    def Done(cls, period: int, course: Course) -> Event:
        """TimeEdit course scraping finished"""

        return cls._create_named_event(period=period, course=course)
