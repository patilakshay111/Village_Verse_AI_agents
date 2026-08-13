from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tick_id: Mapped[int] = mapped_column(Integer, nullable=False)
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    participants: Mapped[str | None] = mapped_column(Text, nullable=True)
    important_moments: Mapped[str | None] = mapped_column(Text, nullable=True)
