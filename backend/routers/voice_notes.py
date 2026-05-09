from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import voice_note as vn_service
from ..repositories import patient as patient_repo
from ..schemas.voice_note import VoiceNoteResponse

router = APIRouter()


@router.get("/api/voice-notes", response_model=list[VoiceNoteResponse])
def list_voice_notes(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    d = target_date or date.today()
    return vn_service.get_by_date(db, d)


@router.post("/api/voice-notes", response_model=VoiceNoteResponse)
async def create_voice_note(
    audio: UploadFile = File(...),
    type: str = Form(...),
    slot: Optional[str] = Form(None),
    med_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    patient = patient_repo.get_first(db)
    note = await vn_service.create_from_audio(db, audio, type, slot, med_id, patient.id)
    return note
