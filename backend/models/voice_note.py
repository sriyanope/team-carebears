from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class VoiceNote(Base):
    __tablename__ = "voice_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"))
    transcript: Mapped[str] = mapped_column(Text)
    categories: Mapped[list] = mapped_column(JSON, default=list)
    ai_tags: Mapped[list] = mapped_column(JSON, default=list)
    severity: Mapped[str] = mapped_column(String(10), default="low")
    note_type: Mapped[str] = mapped_column(String(20), default="adhoc")
    slot: Mapped[str | None] = mapped_column(String(10), nullable=True)
    med_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("medications.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)
