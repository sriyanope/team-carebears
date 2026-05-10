from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MedicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    name: str
    note: Optional[str]
    dosage: Optional[str] = None
    frequency_per_week: Optional[int] = None
    special_instructions: Optional[str] = None
    expiry_date: Optional[date] = None
    time_str: str
    done: bool
    voice_note_text: Optional[str]
    created_at: datetime
    updated_at: datetime


class MedicationUpdate(BaseModel):
    done: bool
    voice_note: Optional[str] = None


class MedicationCreate(BaseModel):
    name: str
    dosage: str
    frequency_per_week: int
    special_instructions: Optional[str] = None
    expiry_date: Optional[date] = None


class MedicationDetailsUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency_per_week: Optional[int] = None
    special_instructions: Optional[str] = None
    expiry_date: Optional[date] = None
