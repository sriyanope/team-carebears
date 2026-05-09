from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class Caregiver(BaseModel):
    id: Optional[str] = None  # Firestore document ID
    name: str
    dob: date
    patient_id: str  # links to patient document
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
