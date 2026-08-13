from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    current_day: Mapped[int] = mapped_column(Integer, default=1)
    current_time: Mapped[str] = mapped_column(String(32), default="Morning")
    tick_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="idle")
    weather: Mapped[str] = mapped_column(String(64), default="Clear")
    last_tick_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    civilization_stage: Mapped[str] = mapped_column(String(64), default="Village")
    technology_level: Mapped[float] = mapped_column(Float, default=0.1)
    gdp: Mapped[float] = mapped_column(Float, default=0.0)
    total_wealth: Mapped[float] = mapped_column(Float, default=0.0)
    unemployment_rate: Mapped[float] = mapped_column(Float, default=0.0)
    economy_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
