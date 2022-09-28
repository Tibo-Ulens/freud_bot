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
