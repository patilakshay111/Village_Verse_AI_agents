from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Rumor(Base):
    __tablename__ = "rumors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rumor_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_agent_id: Mapped[str | None] = mapped_column(
        ForeignKey("villagers.id"), nullable=True
    )
    heard_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    truth_level: Mapped[float] = mapped_column(Float, default=0.7)
    distortion_level: Mapped[float] = mapped_column(Float, default=0.0)
    spread_count: Mapped[int] = mapped_column(Integer, default=1)
    importance: Mapped[float] = mapped_column(Float, default=0.3)
    related_event_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tick_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
