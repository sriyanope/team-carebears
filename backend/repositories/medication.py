from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.medication import Medication


def _to_medication(doc_id: str, data: dict) -> Medication:
    data = dict(data)
    data["id"] = doc_id
    data["created_at"] = normalize_timestamp(data.get("created_at"))
    data["updated_at"] = normalize_timestamp(data.get("updated_at"))
    data.setdefault("dosage", None)
    data.setdefault("frequency_per_week", None)
    data.setdefault("special_instructions", None)
    data.setdefault("expiry_date", None)
    return Medication(**data)


def get_all(db: Session) -> list[Medication]:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = client.collection("medications").order_by("time_str").get()
        meds = []
        for doc in docs:
            meds.append(_to_medication(doc.id, doc.to_dict()))
        return meds
    return db.query(Medication).order_by(Medication.time_str.asc()).all()


def get_by_patient(db: Session, patient_id: str) -> list[Medication]:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = (
            client.collection("medications")
            .where("patient_id", "==", patient_id)
            .order_by("time_str")
            .get()
        )
        meds = []
        for doc in docs:
            meds.append(_to_medication(doc.id, doc.to_dict()))
        return meds
    return (
        db.query(Medication)
        .filter(Medication.patient_id == patient_id)
        .order_by(Medication.time_str.asc())
        .all()
    )


def get_by_id(db: Session, med_id: str) -> Medication | None:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        doc = client.collection("medications").document(med_id).get()
        if not doc.exists:
            return None
        return _to_medication(doc.id, doc.to_dict())
    return db.query(Medication).filter(Medication.id == med_id).first()


def update(db: Session, med: Medication, done: bool, voice_note_text: str | None = None) -> Medication:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        update_payload = {"done": done}
        if voice_note_text is not None:
            update_payload["voice_note_text"] = voice_note_text
        update_payload["updated_at"] = datetime.now(timezone.utc)
        client.collection("medications").document(med.id).update(update_payload)
        med.done = done
        if voice_note_text is not None:
            med.voice_note_text = voice_note_text
        return med
    med.done = done
    if voice_note_text is not None:
        med.voice_note_text = voice_note_text
    db.commit()
    db.refresh(med)
    return med


def create(
    db: Session,
    patient_id: str,
    name: str,
    note: str | None,
    time_str: str,
    dosage: str | None = None,
    frequency_per_week: int | None = None,
    special_instructions: str | None = None,
    expiry_date: date | None = None,
    done: bool = False,
    voice_note_text: str | None = None,
) -> Medication:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        now = datetime.now(timezone.utc)
        payload = {
            "patient_id": patient_id,
            "name": name,
            "note": note,
            "dosage": dosage,
            "frequency_per_week": frequency_per_week,
            "special_instructions": special_instructions,
            "expiry_date": expiry_date.isoformat() if expiry_date else None,
            "time_str": time_str,
            "done": done,
            "voice_note_text": voice_note_text,
            "created_at": now,
            "updated_at": now,
        }
        doc_ref = client.collection("medications").document()
        doc_ref.set(payload)
        payload["id"] = doc_ref.id
        return Medication(**payload)
    med = Medication(
        patient_id=patient_id,
        name=name,
        note=note,
        dosage=dosage,
        frequency_per_week=frequency_per_week,
        special_instructions=special_instructions,
        expiry_date=expiry_date,
        time_str=time_str,
        done=done,
        voice_note_text=voice_note_text,
    )
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


def update_details(
    db: Session,
    med: Medication,
    *,
    updates: dict,
    note: str | None,
) -> Medication:
    if settings.FIREBASE_MODE:
        update_payload = {
            **updates,
            "note": note,
            "updated_at": datetime.now(timezone.utc),
        }
        if isinstance(update_payload.get("expiry_date"), date):
            update_payload["expiry_date"] = update_payload["expiry_date"].isoformat()

        client = get_firestore_client()
        client.collection("medications").document(med.id).update(update_payload)

        for key, value in update_payload.items():
            if key != "updated_at":
                setattr(med, key, value)
        med.updated_at = update_payload["updated_at"]
        return med

    for key, value in updates.items():
        setattr(med, key, value)
    med.note = note
    db.commit()
    db.refresh(med)
    return med


def delete(db: Session, med: Medication) -> None:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        client.collection("medications").document(med.id).delete()
        return

    db.delete(med)
    db.commit()
