from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..repositories import patient as patient_repo
from ..schemas.daily_wellbeing import DailyWellbeingRequest, DailyWellbeingResponse
from ..services import daily_wellbeing as dw_service
from ..services import mock_data

router = APIRouter()


@router.post("/api/daily-wellbeing", response_model=DailyWellbeingResponse)
def create_daily_wellbeing(body: DailyWellbeingRequest):
    if mock_data.is_enabled():
        entries = mock_data.get_daily_wellbeing() or []
        if entries:
            return entries[0]
    patient = patient_repo.get_by_id(None, body.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="No patient found")
    entry = dw_service.create_entry(
        patient_id=patient.id,
        sleep_pattern=body.sleep_pattern,
        appetite=body.appetite,
        mood=body.mood,
        voice_note_id=body.voice_note_id,
    )
    return entry


@router.get("/api/daily-wellbeing", response_model=list[DailyWellbeingResponse])
def list_daily_wellbeing(patient_id: str | None = None, target_date: Optional[date] = None):
    if mock_data.is_enabled():
        return mock_data.get_daily_wellbeing() or []
    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id is required")
    patient = patient_repo.get_by_id(None, patient_id)
    if not patient:
        return []
    if target_date:
        return dw_service.get_entries_by_date(patient.id, target_date)
    return dw_service.get_all_entries(patient.id)
