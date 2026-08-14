from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    module_type: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    # IDs of questions selected for this session.
    # Example: [12, 5, 21, 8, 14]
    question_ids: Mapped[list[int]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Student's current answers.
    # Example:
    # {
    #     "12": "C",
    #     "5": "A",
    #     "21": {"A": 7, "B": 12}
    # }
    answers: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    total_questions: Mapped[int] = mapped_column(
        nullable=False,
    )

    score: Mapped[int | None] = mapped_column(
        nullable=True,
    )
