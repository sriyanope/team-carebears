from datetime import date, datetime, timezone

from sqlalchemy import cast, Date
from sqlalchemy.orm import Session

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
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
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        created = created_at or datetime.now(timezone.utc)
        payload = {
            "patient_id": patient_id,
            "transcript": transcript,
            "categories": categories,
            "ai_tags": ai_tags,
            "severity": severity,
            "note_type": note_type,
            "slot": slot,
            "med_id": med_id,
            "created_at": created,
            "updated_at": created,
            "created_date": created.date().isoformat(),
        }
        doc_ref = client.collection("voice_notes").document()
        doc_ref.set(payload)
        payload["id"] = doc_ref.id
        return VoiceNote(**payload)
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
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = (
            client.collection("voice_notes")
            .where("created_date", "==", target_date.isoformat())
            .get()
        )
        notes = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            data["created_at"] = normalize_timestamp(data.get("created_at"))
            data["updated_at"] = normalize_timestamp(data.get("updated_at"))
            notes.append(VoiceNote(**data))
        notes.sort(key=lambda note: note.created_at)
        return notes
    return (
        db.query(VoiceNote)
        .filter(cast(VoiceNote.created_at, Date) == target_date)
        .order_by(VoiceNote.created_at.asc())
        .all()
    )


def get_by_date_for_patient(db: Session, patient_id: str, target_date: date) -> list[VoiceNote]:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = (
            client.collection("voice_notes")
            .where("patient_id", "==", patient_id)
            .get()
        )
        notes = []
        for doc in docs:
            data = doc.to_dict()
            if data.get("created_date") != target_date.isoformat():
                continue
            data["id"] = doc.id
            data["created_at"] = normalize_timestamp(data.get("created_at"))
            data["updated_at"] = normalize_timestamp(data.get("updated_at"))
            notes.append(VoiceNote(**data))
        notes.sort(key=lambda note: note.created_at)
        return notes
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
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = (
            client.collection("voice_notes")
            .where("created_date", "==", target_date.isoformat())
            .get()
        )
        return len(docs)
    return (
        db.query(VoiceNote)
        .filter(cast(VoiceNote.created_at, Date) == target_date)
        .count()
    )


def get_recent(db: Session, limit: int = 3) -> list[VoiceNote]:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = (
            client.collection("voice_notes")
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
            .get()
        )
        notes = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            data["created_at"] = normalize_timestamp(data.get("created_at"))
            data["updated_at"] = normalize_timestamp(data.get("updated_at"))
            notes.append(VoiceNote(**data))
        return notes
    return (
        db.query(VoiceNote)
        .order_by(VoiceNote.created_at.desc())
        .limit(limit)
        .all()
    )
