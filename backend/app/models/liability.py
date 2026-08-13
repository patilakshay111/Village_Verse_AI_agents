from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Liability(Base):
    __tablename__ = "liabilities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(32), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(64), nullable=False)
    liability_type: Mapped[str] = mapped_column(String(64), nullable=False)
    principal: Mapped[float] = mapped_column(Float, default=0.0)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    interest_rate: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_payment: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(32), default="active")
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    opened_tick: Mapped[int | None] = mapped_column(Integer, nullable=True)
