from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column(ForeignKey("villagers.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    emotion: Mapped[str | None] = mapped_column(String(32), nullable=True)
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    participants: Mapped[str | None] = mapped_column(Text, nullable=True)
    sim_timestamp: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tick_id: Mapped[int | None] = mapped_column(nullable=True)

    agent: Mapped["Villager"] = relationship(back_populates="memories")
