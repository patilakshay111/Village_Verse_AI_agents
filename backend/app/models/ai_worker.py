from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AIWorker(Base):
    __tablename__ = "ai_workers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    worker_type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    productivity: Mapped[float] = mapped_column(Float, default=0.5)
    monthly_cost: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="active")
    hired_tick: Mapped[int | None] = mapped_column(Integer, nullable=True)
