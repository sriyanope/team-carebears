from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.voice_note import VoiceNoteResponse
from ..services import voice_note as vn_service

router = APIRouter()


@router.get("/api/voice-notes", response_model=list[VoiceNoteResponse])
def list_voice_notes(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    d = target_date or date.today()
    return vn_service.get_by_date(db, d)


@router.post("/api/voice-notes", response_model=VoiceNoteResponse)
async def create_voice_note(
    audio: UploadFile = File(...),
    note_type: str = Form(..., alias="type"),
    slot: Optional[str] = Form(None),
    med_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    note = await vn_service.create_from_audio(db, audio, note_type, slot, med_id)
    if note is None:
        raise HTTPException(status_code=404, detail="No patient found")
    return note
