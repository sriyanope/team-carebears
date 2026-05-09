from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.patient import Patient


def get_first(db: Session) -> Patient | None:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = client.collection("patients").limit(1).get()
        if not docs:
            return None
        data = docs[0].to_dict()
        data["id"] = docs[0].id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        return Patient(**data)
    return db.query(Patient).first()


def create(db: Session, name: str, caregiver_name: str) -> Patient:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        doc_ref = client.collection("patients").document()
        now = datetime.now(timezone.utc)
        payload = {
            "name": name,
            "caregiver_name": caregiver_name,
            "created_at": now,
            "updated_at": now,
        }
        doc_ref.set(payload)
        payload["id"] = doc_ref.id
        return Patient(**payload)
    patient = Patient(name=name, caregiver_name=caregiver_name)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
