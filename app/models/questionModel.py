from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


# The class will have module type for differentiation and data, solution as JSONB for different structures
class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    module_type: Mapped[str] = mapped_column(String(60))
    difficulty: Mapped[str] = mapped_column(String(60))
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    solution: Mapped[dict] = mapped_column(JSONB, nullable=False)
