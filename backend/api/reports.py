from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.patient import Patient
from ..repositories import patient as patient_repo
from ..repositories import report as report_repo
from ..schemas.report import ReportDetailResponse, ReportGenerateRequest, ReportSummaryResponse
from ..services import mock_data
from ..services.report import generate_report

router = APIRouter()


def _normalize_name(value: str | None) -> str:
    return (value or "").strip().casefold()


def _patient_from_doc(doc_id: str, data: dict) -> Patient:
    caregiver_name = data.get("caregiver_name")
    if caregiver_name is None and isinstance(data.get("caregiver"), dict):
        caregiver_name = data["caregiver"].get("name")

    patient_name = data.get("name")
    if patient_name is None and isinstance(data.get("patient"), dict):
        patient_name = data["patient"].get("name")

    return Patient(
        id=doc_id,
        name=patient_name or "",
        caregiver_name=caregiver_name or "",
        created_at=normalize_timestamp(data.get("created_at")),
        updated_at=normalize_timestamp(data.get("updated_at")),
    )


def _resolve_patient(
    patient_id: str | None = None,
    caregiver_name: str | None = None,
    patient_name: str | None = None,
) -> Patient | None:
    if patient_id:
        return patient_repo.get_by_id(None, patient_id)
    if not settings.FIREBASE_MODE:
        return patient_repo.get_first(None)

    normalized_caregiver = _normalize_name(caregiver_name)
    normalized_patient = _normalize_name(patient_name)

    if not normalized_caregiver and not normalized_patient:
        return patient_repo.get_first(None)

    client = get_firestore_client()
    matches: list[Patient] = []
    for doc in client.collection("patients").stream():
        patient = _patient_from_doc(doc.id, doc.to_dict() or {})
        if normalized_caregiver and _normalize_name(patient.caregiver_name) != normalized_caregiver:
            continue
        if normalized_patient and _normalize_name(patient.name) != normalized_patient:
            continue
        matches.append(patient)

    matches.sort(
        key=lambda patient: patient.updated_at or patient.created_at or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return matches[0] if matches else None


@router.get("/api/reports", response_model=list[ReportSummaryResponse])
def list_reports(
    patient_id: str | None = None,
    caregiver_name: str | None = None,
    patient_name: str | None = None,
):
    if mock_data.is_enabled():
        return mock_data.get_reports() or []
    patient = _resolve_patient(patient_id, caregiver_name, patient_name)
    if patient is None or not patient.id:
        return []
    return report_repo.get_all(patient.id)


@router.post("/api/reports", response_model=ReportDetailResponse)
async def create_report(body: ReportGenerateRequest):
    if body.start_date > body.end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")
    patient = _resolve_patient(body.patient_id, body.caregiver_name, body.patient_name)
    if patient is None or not patient.id:
        raise HTTPException(status_code=404, detail="No patient found")
    return await generate_report(patient.id, body.start_date, body.end_date)


@router.get("/api/reports/{report_id}", response_model=ReportDetailResponse)
def get_report(
    report_id: str,
    patient_id: str | None = None,
    caregiver_name: str | None = None,
    patient_name: str | None = None,
):
    if mock_data.is_enabled():
        report = mock_data.get_report(report_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found")
        return report

    report = report_repo.get_by_id(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    patient = _resolve_patient(patient_id, caregiver_name, patient_name)
    if patient is not None and patient.id and report.patient_id != patient.id:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
