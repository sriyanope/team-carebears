from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VoiceNote(BaseModel):
    id: Optional[str] = None
    patient_id: str
    transcript: str
    note_type: str = "adhoc"  # "adhoc" | "daily_wellbeing" | "medication"
    language: str = "en"      # "en" | "zh" | "ms" | "ta"
    med_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
