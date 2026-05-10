from datetime import date, datetime, timezone

from google.cloud.firestore_v1.base_query import FieldFilter

from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.daily_wellbeing import DailyWellbeing

COLLECTION = "daily_wellbeing"


def create(entry: DailyWellbeing) -> DailyWellbeing:
    client = get_firestore_client()
    now = datetime.now(timezone.utc)
    payload = {
        "patient_id": entry.patient_id,
        "date": str(entry.date),
        "sleep_pattern": entry.sleep_pattern,
        "appetite": entry.appetite,
        "mood": entry.mood,
        "voice_note_id": entry.voice_note_id,
        "created_at": now,
        "updated_at": now,
    }
    doc_ref = client.collection(COLLECTION).document()
    doc_ref.set(payload)
    entry.id = doc_ref.id
    entry.created_at = now
    entry.updated_at = now
    return entry


def get_by_date(patient_id: str, target_date: date) -> list[DailyWellbeing]:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .where(filter=FieldFilter("date", "==", str(target_date)))
        .stream()
    )
    entries = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        entries.append(DailyWellbeing(**data))
    return entries


def get_by_date_range(patient_id: str, start_date: date, end_date: date) -> list[DailyWellbeing]:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .stream()
    )
    entries = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        entry = DailyWellbeing(**data)
        if start_date <= entry.date <= end_date:
            entries.append(entry)
    entries.sort(key=lambda e: e.date)
    return entries


def get_all(patient_id: str) -> list[DailyWellbeing]:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .order_by("date", direction="DESCENDING")
        .stream()
    )
    entries = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        entries.append(DailyWellbeing(**data))
    return entries
