from datetime import datetime, timezone

from google.cloud.firestore_v1.base_query import FieldFilter

from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.report import Report

COLLECTION = "reports"


def _normalize_flags(raw_flags: list) -> list[dict]:
    normalized: list[dict] = []
    for item in raw_flags:
        if not isinstance(item, dict):
            continue
        what = item.get("what")
        why = item.get("why")
        legacy_text = item.get("text")
        if isinstance(what, str) and what.strip() and isinstance(why, str) and why.strip():
            normalized.append({"what": what.strip(), "why": why.strip()})
        elif isinstance(legacy_text, str) and legacy_text.strip():
            normalized.append(
                {
                    "what": legacy_text.strip(),
                    "why": "Mention this observation during the next doctor visit.",
                }
            )
    return normalized


def _to_report(doc_id: str, data: dict) -> Report:
    summary_narrative = data.get("summary_narrative") or data.get("summary") or ""
    summary_bullets = data.get("summary_bullets") or []
    if not summary_bullets and summary_narrative:
        summary_bullets = [{"text": summary_narrative, "references": []}]
    payload = {
        "id": doc_id,
        "patient_id": data.get("patient_id", ""),
        "title": data.get("title", ""),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "summary_narrative": summary_narrative,
        "summary_bullets": summary_bullets,
        "flags": _normalize_flags(data.get("flags", [])),
        "language": data.get("language", "en"),
        "audio_storage_path": data.get("audio_storage_path"),
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
        "summary_narrative": report.summary_narrative,
        "summary_bullets": [item.model_dump() for item in report.summary_bullets],
        "flags": [f.model_dump() for f in report.flags],
        "language": report.language,
        "audio_storage_path": report.audio_storage_path,
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


def update_audio_storage_path(report_id: str, audio_storage_path: str) -> Report | None:
    client = get_firestore_client()
    doc_ref = client.collection(COLLECTION).document(report_id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        return None
    doc_ref.update(
        {
            "audio_storage_path": audio_storage_path,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    refreshed = doc_ref.get()
    return _to_report(refreshed.id, refreshed.to_dict())


def count(patient_id: str) -> int:
    client = get_firestore_client()
    docs = (
        client.collection(COLLECTION)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .stream()
    )
    return sum(1 for _ in docs)
