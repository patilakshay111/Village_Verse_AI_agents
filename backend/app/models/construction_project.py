from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ConstructionProject(Base):
    __tablename__ = "construction_projects"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(32), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False)
    project_type: Mapped[str] = mapped_column(String(64), nullable=False)
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    spent: Mapped[float] = mapped_column(Float, default=0.0)
    duration_days: Mapped[int] = mapped_column(Integer, default=30)
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    roi_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="planned")
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_tick: Mapped[int | None] = mapped_column(Integer, nullable=True)
