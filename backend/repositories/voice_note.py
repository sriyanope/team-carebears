from datetime import date, datetime
from sqlalchemy import cast, Date
from sqlalchemy.orm import Session
from ..models.voice_note import VoiceNote


def create(
    db: Session,
    patient_id: str,
    transcript: str,
    categories: list,
    ai_tags: list,
    severity: str,
    note_type: str,
    slot: str | None = None,
    med_id: str | None = None,
    created_at: datetime | None = None,
) -> VoiceNote:
    kwargs: dict = dict(
        patient_id=patient_id,
        transcript=transcript,
        categories=categories,
        ai_tags=ai_tags,
        severity=severity,
        note_type=note_type,
        slot=slot,
        med_id=med_id,
    )
    if created_at is not None:
        kwargs["created_at"] = created_at
        kwargs["updated_at"] = created_at
    note = VoiceNote(**kwargs)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_by_date(db: Session, target_date: date) -> list[VoiceNote]:
    return (
        db.query(VoiceNote)
        .filter(cast(VoiceNote.created_at, Date) == target_date)
        .order_by(VoiceNote.created_at.asc())
        .all()
    )


def get_by_date_for_patient(db: Session, patient_id: str, target_date: date) -> list[VoiceNote]:
    return (
        db.query(VoiceNote)
        .filter(
            VoiceNote.patient_id == patient_id,
            cast(VoiceNote.created_at, Date) == target_date,
        )
        .order_by(VoiceNote.created_at.asc())
        .all()
    )


def count_by_date(db: Session, target_date: date) -> int:
    return (
        db.query(VoiceNote)
        .filter(cast(VoiceNote.created_at, Date) == target_date)
        .count()
    )


def get_recent(db: Session, limit: int = 3) -> list[VoiceNote]:
    return (
        db.query(VoiceNote)
        .order_by(VoiceNote.created_at.desc())
        .limit(limit)
        .all()
    )
