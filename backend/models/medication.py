from datetime import date, datetime, timezone
from uuid import uuid4
from sqlalchemy import String, Boolean, Text, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"))
    name: Mapped[str] = mapped_column(String(200))
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    frequency_per_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    time_str: Mapped[str] = mapped_column(String(5), default="08:00")
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    voice_note_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)
