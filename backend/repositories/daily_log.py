from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.daily_log import DailyLog


def get_by_date(db: Session, patient_id: str, target_date: date) -> DailyLog | None:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        doc_id = f"{patient_id}_{target_date.isoformat()}"
        doc = client.collection("daily_logs").document(doc_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        if isinstance(data.get("date"), str):
            data["date"] = date.fromisoformat(data["date"])
        return DailyLog(**data)
    return (
        db.query(DailyLog)
        .filter(DailyLog.patient_id == patient_id, DailyLog.date == target_date)
        .first()
    )


def upsert(db: Session, patient_id: str, target_date: date, **fields) -> DailyLog:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        doc_id = f"{patient_id}_{target_date.isoformat()}"
        now = datetime.now(timezone.utc)
        payload = {"patient_id": patient_id, "date": target_date.isoformat(), **fields}
        payload.setdefault("created_at", now)
        payload.setdefault("updated_at", now)
        client.collection("daily_logs").document(doc_id).set(payload, merge=True)
        payload["id"] = doc_id
        payload["date"] = target_date
        return DailyLog(**payload)
    log = get_by_date(db, patient_id, target_date)
    if log is None:
        log = DailyLog(id=str(uuid4()), patient_id=patient_id, date=target_date)
        db.add(log)
    for key, value in fields.items():
        if value is not None:
            setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log
