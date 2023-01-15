from discord import User, Member

from bot.events import Event
from bot.models.course import Course
from bot import util


class CourseEvent(Event):
    """Events related to courses"""

    scope = "course"

    @classmethod
    def course_added(cls, course: Course) -> Event:
        """Added a course"""

        return cls._create_named_event(user_msg=f"Added course {course}", course=course)

    @classmethod
    def course_removed(cls, course: Course) -> Event:
        """Removed a course"""

        return cls._create_named_event(
            user_msg=f"Removed course {course}", course=course
        )

    @classmethod
    def course_enrolled(cls, user: User | Member, course: Course) -> Event:
        """A user enrolled in a course"""

        return cls._create_named_event(
            user_msg=f"You have enrolled in the course {course}",
            user=util.render_user(user),
            course=course,
        )

    @classmethod
    def course_dropped(cls, user: User | Member, course: Course) -> Event:
        """A user dropped a course"""

        return cls._create_named_event(
            user_msg=f"You have dropped the course {course}",
            user=util.render_user(user),
            course=course,
        )


class LectureInfoEvent(Event):
    """Events emitted when handling lecture info"""

    scope = "lecture info"

    @classmethod
    def deleting_old_lecture_info(cls, course: Course) -> Event:
        """Started deleting old lecture info"""

        return cls._create_named_event(
            user_msg=f"Deleting old lecture info for course {course}", course=course
        )

    @classmethod
    def refreshed_lecture_info(cls, course: Course) -> Event:
        """Refreshed lecture info"""

        return cls._create_named_event(
            user_msg=f"Refreshed lecture info for course {course}", course=course
        )

    @classmethod
    def searching_lecture_info(cls, course: Course) -> Event:
        """Started searching for lecture info"""

        return cls._create_named_event(
            user_msg=f"Searching lecture info for course {course} (this may take a while)",
            course=course,
        )

    @classmethod
    def downloading_lecture_info(cls, course: Course) -> Event:
        """Started downloading lecture info"""

        return cls._create_named_event(
            user_msg=f"Downloading lecture info for course {course}", course=course
        )

    @classmethod
    def storing_lecture_info(cls, course: Course) -> Event:
        """Started storing lecture info"""

        return cls._create_named_event(
            user_msg=f"Storing lecture info for course {course}", course=course
        )


class TimeEditEvent(Event):
    """Events emitted while scraping TimeEdit"""

    scope = "timeedit"

    @classmethod
    def searching_course(cls, period: int, course: Course) -> Event:
        """A course was searched on TimeEdit"""

        return cls._create_named_event(period=period, course=course)

    @classmethod
    def added_course(cls, period: int, course: Course) -> Event:
        """A course was added on TimeEdit"""

        return cls._create_named_event(period=period, course=course)

    @classmethod
    def course_not_found(cls, period: int, course: Course) -> Event:
        """A course was not found on TimeEdit"""

        return cls._create_named_event(period=period, course=course)

    @classmethod
    def done(cls, period: int, course: Course) -> Event:
        """TimeEdit course scraping finished"""

        return cls._create_named_event(period=period, course=course)
