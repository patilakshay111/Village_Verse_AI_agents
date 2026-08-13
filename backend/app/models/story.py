from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    story_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    tick_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    full_story: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    time: Mapped[str | None] = mapped_column(String(32), nullable=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    participants: Mapped[str | None] = mapped_column(Text, nullable=True)
    families: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    relationship_changes: Mapped[str | None] = mapped_column(Text, nullable=True)
    future_hooks: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_story_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
