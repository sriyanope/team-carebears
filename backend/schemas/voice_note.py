from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class VoiceNoteResponse(BaseModel):
    id: str
    patient_id: str
    transcript: str
    note_type: str
    language: str
    med_id: Optional[str]
    created_at: datetime
    updated_at: datetime
