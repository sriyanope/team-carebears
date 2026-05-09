from datetime import date, datetime, timezone

from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.voice_note import VoiceNote

COLLECTION = "voice_notes"


def create(
    patient_id: str,
    transcript: str,
    note_type: str = "adhoc",
    language: str = "en",
    med_id: str | None = None,
) -> VoiceNote:
    client = get_firestore_client()
    now = datetime.now(timezone.utc)
    payload = {
        "patient_id": patient_id,
        "transcript": transcript,
        "note_type": note_type,
        "language": language,
        "med_id": med_id,
        "date": now.date().isoformat(),  # stored for easy date filtering
        "created_at": now,
        "updated_at": now,
    }
    doc_ref = client.collection(COLLECTION).document()
    doc_ref.set(payload)
    return VoiceNote(
        id=doc_ref.id,
        patient_id=patient_id,
        transcript=transcript,
        note_type=note_type,
        language=language,
        med_id=med_id,
        created_at=now,
        updated_at=now,
    )


def get_all(patient_id: str) -> list[VoiceNote]:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where("patient_id", "==", patient_id)
        .order_by("created_at", direction="DESCENDING")
        .stream()
    )
    notes = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        notes.append(VoiceNote(**data))
    return notes


def get_by_date(patient_id: str, target_date: date) -> list[VoiceNote]:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where("patient_id", "==", patient_id)
        .where("date", "==", target_date.isoformat())
        .stream()
    )
    notes = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        notes.append(VoiceNote(**data))
    notes.sort(key=lambda n: n.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return notes


def get_by_date_range(patient_id: str, start_date: date, end_date: date) -> list[VoiceNote]:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where("patient_id", "==", patient_id)
        .where("date", ">=", start_date.isoformat())
        .where("date", "<=", end_date.isoformat())
        .stream()
    )
    notes = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        notes.append(VoiceNote(**data))
    notes.sort(key=lambda n: n.created_at or datetime.min.replace(tzinfo=timezone.utc))
    return notes


def get_by_id(note_id: str) -> VoiceNote | None:
    client = get_firestore_client()
    doc = client.collection(COLLECTION).document(note_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    data["created_at"] = normalize_timestamp(data.get("created_at"))
    data["updated_at"] = normalize_timestamp(data.get("updated_at"))
    return VoiceNote(**data)
