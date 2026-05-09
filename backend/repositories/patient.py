from datetime import datetime, timezone

from sqlalchemy.orm import Session
from firebase_admin import firestore

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.patient import Patient


def _to_patient(doc_id: str, data: dict) -> Patient:
    caregiver_name = data.get("caregiver_name")
    if caregiver_name is None and isinstance(data.get("caregiver"), dict):
        caregiver_name = data["caregiver"].get("name")

    name = data.get("name")
    if name is None and isinstance(data.get("patient"), dict):
        name = data["patient"].get("name")

    patient_data = {
        "id": doc_id,
        "name": name or "",
        "caregiver_name": caregiver_name or "",
        "created_at": normalize_timestamp(data.get("created_at")),
        "updated_at": normalize_timestamp(data.get("updated_at")),
    }
    return Patient(**patient_data)


def get_first(db: Session) -> Patient | None:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        docs = (
            client.collection("patients")
            .order_by("updated_at", direction=firestore.Query.DESCENDING)
            .limit(1)
            .get()
        )
        if not docs:
            return None
        data = docs[0].to_dict()
        return _to_patient(docs[0].id, data)
    return db.query(Patient).order_by(Patient.updated_at.desc()).first()


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


def update(
    db: Session,
    patient: Patient,
    *,
    name: str | None = None,
    caregiver_name: str | None = None,
) -> Patient:
    next_name = name if name is not None else patient.name
    next_caregiver_name = caregiver_name if caregiver_name is not None else patient.caregiver_name

    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        doc_ref = client.collection("patients").document(patient.id)
        now = datetime.now(timezone.utc)
        payload = {
            "name": next_name,
            "caregiver_name": next_caregiver_name,
            "updated_at": now,
        }
        doc_ref.set(payload, merge=True)
        return Patient(
            id=patient.id,
            name=next_name,
            caregiver_name=next_caregiver_name,
            created_at=patient.created_at,
            updated_at=now,
        )

    patient.name = next_name
    patient.caregiver_name = next_caregiver_name
    db.commit()
    db.refresh(patient)
    return patient


def upsert_profile(db: Session, *, name: str, caregiver_name: str) -> Patient:
    patient = get_first(db)
    if patient is None:
        return create(db, name, caregiver_name)
    return update(db, patient, name=name, caregiver_name=caregiver_name)
