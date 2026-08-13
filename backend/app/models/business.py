from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    business_type: Mapped[str] = mapped_column(String(64), nullable=False)
    owner_id: Mapped[str] = mapped_column(ForeignKey("villagers.id"), nullable=False)
    organization_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    cash: Mapped[float] = mapped_column(Float, default=0.0)
    revenue_monthly: Mapped[float] = mapped_column(Float, default=0.0)
    expenses_monthly: Mapped[float] = mapped_column(Float, default=0.0)
    employee_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="active")
    founded_tick: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
