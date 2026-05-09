from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class DailyWellbeingRequest(BaseModel):
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
    created_at: datetime
