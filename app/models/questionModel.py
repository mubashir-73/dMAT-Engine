from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Question(Base):
    __tablename__ = "Questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_type: Mapped[str] = mapped_column(String(60))
    difficulty_level: Mapped[str] = mapped_column(String(60))
    options: Mapped[list["Option"]] = relationship(
        back_populates="Questions", cascade="all, delete-orphan"
    )


#    correctOptions: Mapped[list["Option"]] = relationship()


class Option(Base):
    __tablename__ = "Options"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("Questions.id"))


# class Content(Base):

# TODO: Make proper schema and use alembic to version it
