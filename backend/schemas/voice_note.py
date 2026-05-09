from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class VoiceNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    transcript: str
    categories: list[str]
    ai_tags: list[str]
    severity: str
    note_type: str
    slot: Optional[str]
    med_id: Optional[str]
    created_at: datetime
    updated_at: datetime
