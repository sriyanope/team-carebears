from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MedicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    name: str
    note: Optional[str]
    time_str: str
    done: bool
    voice_note_text: Optional[str]
    created_at: datetime
    updated_at: datetime


class MedicationUpdate(BaseModel):
    done: bool
    voice_note: Optional[str] = None
