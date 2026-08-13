import json
from typing import Any

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Villager(Base):
    __tablename__ = "villagers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    occupation: Mapped[str] = mapped_column(String(64), nullable=False)
    education: Mapped[str | None] = mapped_column(String(64), nullable=True)
    family_id: Mapped[str] = mapped_column(ForeignKey("families.id"), nullable=False)
    location_id: Mapped[str | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    personality: Mapped[str | None] = mapped_column(Text, nullable=True)
    humor_style: Mapped[str | None] = mapped_column(String(64), nullable=True)
    temperament: Mapped[str | None] = mapped_column(String(64), nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    fears: Mapped[str | None] = mapped_column(Text, nullable=True)
    dreams: Mapped[str | None] = mapped_column(Text, nullable=True)
    hobbies: Mapped[str | None] = mapped_column(Text, nullable=True)
    financial_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    social_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    daily_schedule: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_emotion: Mapped[str] = mapped_column(String(32), default="Neutral")
    emotion_intensity: Mapped[float] = mapped_column(Float, default=0.3)
    # Civilization engine fields
    agent_role: Mapped[str] = mapped_column(String(64), default="villager")
    cash: Mapped[float] = mapped_column(Float, default=0.0)
    bank_balance: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_income: Mapped[float] = mapped_column(Float, default=0.0)
    monthly_expenses: Mapped[float] = mapped_column(Float, default=0.0)
    net_worth: Mapped[float] = mapped_column(Float, default=0.0)
    reputation: Mapped[float] = mapped_column(Float, default=50.0)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    intelligence: Mapped[float] = mapped_column(Float, default=0.5)
    employment_status: Mapped[str] = mapped_column(String(32), default="employed")
    active_goal_plan: Mapped[str | None] = mapped_column(Text, nullable=True)

    family: Mapped["Family"] = relationship(back_populates="members")
    location: Mapped["Location | None"] = relationship(back_populates="villagers")
    memories: Mapped[list["Memory"]] = relationship(back_populates="agent")

    def personality_list(self) -> list[str]:
        if not self.personality:
            return []
        try:
            data = json.loads(self.personality)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    def set_json_field(self, field: str, value: Any) -> None:
        setattr(self, field, json.dumps(value))
