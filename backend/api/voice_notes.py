from datetime import date
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..schemas.voice_note import VoiceNoteResponse
from ..services import mock_data
from ..services import voice_note as vn_service

router = APIRouter()


@router.get("/api/voice-notes", response_model=list[VoiceNoteResponse])
def list_voice_notes(patient_id: str | None = None, target_date: Optional[date] = None):
    if mock_data.is_enabled():
        return mock_data.get_voice_notes() or []
    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id is required")
    if target_date:
        return vn_service.get_by_date(patient_id, target_date)
    return vn_service.get_all(patient_id)


@router.post("/api/voice-notes", response_model=VoiceNoteResponse)
async def create_voice_note(
    audio: UploadFile = File(...),
    note_type: str = Form(..., alias="type"),
    language: str = Form("en"),
    med_id: Optional[str] = Form(None),
    patient_id: str = Form(...),
):
    note = await vn_service.create_from_audio(audio, note_type, language, med_id, patient_id)
    if note is None:
        raise HTTPException(status_code=404, detail="No patient found")
    return note
