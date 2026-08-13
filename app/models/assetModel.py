from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.db.database import Base


# Images will be stored here
class Assets(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"),
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    width: Mapped[int | None] = mapped_column()
    height: Mapped[int | None] = mapped_column()
    alt_text: Mapped[str | None] = mapped_column(String(255))
