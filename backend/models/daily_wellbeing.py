from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class DailyWellbeing(BaseModel):
    id: Optional[str] = None  # Firestore document ID
    patient_id: str
    date: date
    sleep_pattern: str  # "earlier_sleep_later_wake" | "same" | "later_sleep_earlier_wake"
    appetite: str       # "eating_less" | "same" | "eating_more"
    mood: str           # "happy" | "ok" | "neutral" | "sad" | "upset"
    voice_note_id: Optional[str] = None  # optional linked voice note
    voice_note_transcript: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
