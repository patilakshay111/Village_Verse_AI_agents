from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Family(Base):
    __tablename__ = "families"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    surname: Mapped[str] = mapped_column(String(64), nullable=False)
    reputation: Mapped[float] = mapped_column(Float, default=50.0)
    wealth: Mapped[float] = mapped_column(Float, default=50.0)
    influence: Mapped[float] = mapped_column(Float, default=50.0)
    traditions: Mapped[str | None] = mapped_column(Text, nullable=True)

    members: Mapped[list["Villager"]] = relationship(back_populates="family")
