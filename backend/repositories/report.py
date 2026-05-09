from datetime import datetime, timezone

from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.report import Report

COLLECTION = "reports"


def create(report: Report) -> Report:
    client = get_firestore_client()
    now = datetime.now(timezone.utc)
    payload = {
        "patient_id": report.patient_id,
        "title": report.title,
        "start_date": str(report.start_date),
        "end_date": str(report.end_date),
        "summary": report.summary,
        "flags": [f.model_dump() for f in report.flags],
        "generated_at": report.generated_at or now,
        "created_at": now,
        "updated_at": now,
    }
    doc_ref = client.collection(COLLECTION).document()
    doc_ref.set(payload)
    report.id = doc_ref.id
    report.created_at = now
    report.updated_at = now
    return report


def get_all(patient_id: str) -> list[Report]:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where("patient_id", "==", patient_id)
        .order_by("generated_at", direction="DESCENDING")
        .stream()
    )
    reports = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        data["created_at"] = normalize_timestamp(data.get("created_at"))
        data["updated_at"] = normalize_timestamp(data.get("updated_at"))
        data["generated_at"] = normalize_timestamp(data.get("generated_at"))
        reports.append(Report(**data))
    return reports


def get_by_id(report_id: str) -> Report | None:
    client = get_firestore_client()
    doc = client.collection(COLLECTION).document(report_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    data["created_at"] = normalize_timestamp(data.get("created_at"))
    data["updated_at"] = normalize_timestamp(data.get("updated_at"))
    data["generated_at"] = normalize_timestamp(data.get("generated_at"))
    return Report(**data)
