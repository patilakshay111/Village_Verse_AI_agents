from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    market_id: Mapped[str] = mapped_column(ForeignKey("markets.id"), nullable=False)
    commodity: Mapped[str] = mapped_column(String(64), nullable=False)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    supply: Mapped[float] = mapped_column(Float, default=100.0)
    demand: Mapped[float] = mapped_column(Float, default=100.0)
    tick_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
