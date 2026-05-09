from datetime import datetime, timezone, date
from uuid import uuid4
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DailyLog(Base):
    __tablename__ = "daily_logs"

    __table_args__ = (UniqueConstraint("patient_id", "date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"))
    date: Mapped[date] = mapped_column(Date)
    mood: Mapped[int | None] = mapped_column(Integer, nullable=True)
    food_breakfast: Mapped[int] = mapped_column(Integer, default=0)
    food_lunch: Mapped[int] = mapped_column(Integer, default=0)
    food_dinner: Mapped[int] = mapped_column(Integer, default=0)
    hydration: Mapped[int] = mapped_column(Integer, default=0)
    confusion: Mapped[str] = mapped_column(String(20), default="None")
    agitation: Mapped[str] = mapped_column(String(20), default="None")
    wandering: Mapped[str] = mapped_column(String(20), default="No")
    recognition: Mapped[str] = mapped_column(String(20), default="Normal")
    hallucinations: Mapped[str] = mapped_column(String(20), default="None")
    sleep_disruptions: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)
