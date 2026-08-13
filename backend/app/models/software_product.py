from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SoftwareProduct(Base):
    __tablename__ = "software_products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    problem_solved: Mapped[str | None] = mapped_column(Text, nullable=True)
    mvp_features: Mapped[str | None] = mapped_column(Text, nullable=True)
    revenue_model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    development_cost: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="idea")
    launched_tick: Mapped[int | None] = mapped_column(Integer, nullable=True)
