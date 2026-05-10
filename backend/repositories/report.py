from datetime import datetime, timezone

from google.cloud.firestore_v1.base_query import FieldFilter

from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.report import Report

COLLECTION = "reports"


def _to_report(doc_id: str, data: dict) -> Report:
    payload = {
        "id": doc_id,
        "patient_id": data.get("patient_id", ""),
        "title": data.get("title", ""),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "summary": data.get("summary"),
        "flags": data.get("flags", []),
        "generated_at": normalize_timestamp(data.get("generated_at")),
        "created_at": normalize_timestamp(data.get("created_at")),
        "updated_at": normalize_timestamp(data.get("updated_at")),
    }
    return Report(**payload)


def create(report: Report) -> Report:
    client = get_firestore_client()
    now = datetime.now(timezone.utc)
    generated_at = report.generated_at or now
    payload = {
        "patient_id": report.patient_id,
        "title": report.title,
        "start_date": report.start_date.isoformat(),
        "end_date": report.end_date.isoformat(),
        "summary": report.summary or "",
        "flags": [f.model_dump() for f in report.flags],
        "generated_at": generated_at,
        "created_at": now,
        "updated_at": now,
    }
    doc_ref = client.collection(COLLECTION).document()
    doc_ref.set(payload)
    report.id = doc_ref.id
    report.generated_at = generated_at
    report.created_at = now
    report.updated_at = now
    return report


def get_all(patient_id: str) -> list[Report]:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .stream()
    )
    reports = []
    for doc in docs:
        reports.append(_to_report(doc.id, doc.to_dict()))
    reports.sort(
        key=lambda report: report.created_at or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return reports


def get_by_id(report_id: str) -> Report | None:
    client = get_firestore_client()
    doc = client.collection(COLLECTION).document(report_id).get()
    if not doc.exists:
        return None
    return _to_report(doc.id, doc.to_dict())


def count(patient_id: str) -> int:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .stream()
    )
    return sum(1 for _ in docs)
