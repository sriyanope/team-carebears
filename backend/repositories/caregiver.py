from datetime import datetime, timezone

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from google.cloud.firestore_v1.base_query import FieldFilter

from ..models.caregiver import Caregiver

COLLECTION = "caregivers"


def _to_caregiver(doc_id: str, data: dict) -> Caregiver:
    payload = {
        "id": doc_id,
        "name": data.get("name", ""),
        "dob": data.get("dob"),
        "patient_id": data.get("patient_id", ""),
        "created_at": normalize_timestamp(data.get("created_at")),
        "updated_at": normalize_timestamp(data.get("updated_at")),
    }
    return Caregiver(**payload)


def get_by_id(caregiver_id: str) -> Caregiver | None:
    if not settings.FIREBASE_MODE:
        return None
    client = get_firestore_client()
    doc = client.collection(COLLECTION).document(caregiver_id).get()
    if not doc.exists:
        return None
    return _to_caregiver(doc.id, doc.to_dict() or {})


def get_by_patient_id(patient_id: str) -> Caregiver | None:
    if not settings.FIREBASE_MODE:
        return None
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .limit(1)
        .get()
    )
    if not docs:
        return None
    return _to_caregiver(docs[0].id, docs[0].to_dict() or {})


def create(*, name: str, patient_id: str, dob=None) -> Caregiver:
    if not settings.FIREBASE_MODE:
        raise ValueError("Caregiver repository requires FIREBASE_MODE")
    client = get_firestore_client()
    now = datetime.now(timezone.utc)
    payload = {
        "name": name,
        "dob": dob,
        "patient_id": patient_id,
        "created_at": now,
        "updated_at": now,
    }
    doc_ref = client.collection(COLLECTION).document()
    doc_ref.set(payload)
    return Caregiver(
        id=doc_ref.id,
        name=name,
        dob=dob,
        patient_id=patient_id,
        created_at=now,
        updated_at=now,
    )


def update(
    caregiver: Caregiver,
    *,
    name: str | None = None,
    dob=None,
) -> Caregiver:
    if not settings.FIREBASE_MODE:
        return caregiver
    client = get_firestore_client()
    next_name = name if name is not None else caregiver.name
    next_dob = dob if dob is not None else caregiver.dob
    now = datetime.now(timezone.utc)
    payload = {
        "name": next_name,
        "dob": next_dob,
        "updated_at": now,
    }
    client.collection(COLLECTION).document(caregiver.id).set(payload, merge=True)
    return Caregiver(
        id=caregiver.id,
        name=next_name,
        dob=next_dob,
        patient_id=caregiver.patient_id,
        created_at=caregiver.created_at,
        updated_at=now,
    )
