from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(32), nullable=False)  # villager | organization | family
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_cost: Mapped[float] = mapped_column(Float, default=0.0)
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    acquired_tick: Mapped[int | None] = mapped_column(Integer, nullable=True)
