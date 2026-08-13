from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_a_id: Mapped[str] = mapped_column(ForeignKey("villagers.id"), nullable=False)
    agent_b_id: Mapped[str] = mapped_column(ForeignKey("villagers.id"), nullable=False)
    friendship: Mapped[float] = mapped_column(Float, default=0.0)
    trust: Mapped[float] = mapped_column(Float, default=0.0)
    respect: Mapped[float] = mapped_column(Float, default=0.0)
    rivalry: Mapped[float] = mapped_column(Float, default=0.0)
    romantic_interest: Mapped[float] = mapped_column(Float, default=0.0)
    family_bond: Mapped[float] = mapped_column(Float, default=0.0)
    last_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
