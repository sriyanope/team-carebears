from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class DailyWellbeingRequest(BaseModel):
    patient_id: str
    sleep_pattern: str  # "earlier_sleep_later_wake" | "same" | "later_sleep_earlier_wake"
    appetite: str       # "eating_less" | "same" | "eating_more"
    mood: str           # "happy" | "ok" | "neutral" | "sad" | "upset"
    voice_note_id: Optional[str] = None


class DailyWellbeingResponse(BaseModel):
    id: str
    patient_id: str
    date: date
    sleep_pattern: str
    appetite: str
    mood: str
    voice_note_id: Optional[str]
    voice_note_transcript: Optional[str] = None
    created_at: datetime
