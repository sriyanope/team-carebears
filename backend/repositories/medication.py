from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.medication import Medication


def get_all(db: Session) -> list[Medication]:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = client.collection("medications").order_by("time_str").get()
        meds = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            data["created_at"] = normalize_timestamp(data.get("created_at"))
            data["updated_at"] = normalize_timestamp(data.get("updated_at"))
            meds.append(Medication(**data))
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
            data = doc.to_dict()
            data["id"] = doc.id
            data["created_at"] = normalize_timestamp(data.get("created_at"))
            data["updated_at"] = normalize_timestamp(data.get("updated_at"))
            meds.append(Medication(**data))
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
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        return Medication(**data)
    return db.query(Medication).filter(Medication.id == med_id).first()


def update(db: Session, med: Medication, done: bool, voice_note_text: str | None = None) -> Medication:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        update_payload = {"done": done}
        if voice_note_text is not None:
            update_payload["voice_note_text"] = voice_note_text
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
        time_str=time_str,
        done=done,
        voice_note_text=voice_note_text,
    )
    db.add(med)
    return med
