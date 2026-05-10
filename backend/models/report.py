from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ReportReference(BaseModel):
    date_label: str
    source_type: str


class ReportSummaryBullet(BaseModel):
    text: str
    references: List[ReportReference] = Field(default_factory=list)


class ReportFlag(BaseModel):
    what: str
    why: str


class Report(BaseModel):
    id: Optional[str] = None  # Firestore document ID
    patient_id: str
    title: str
    start_date: date
    end_date: date
    summary_narrative: str = ""
    summary_bullets: List[ReportSummaryBullet] = Field(default_factory=list)
    flags: List[ReportFlag] = Field(default_factory=list)
    language: str = "en"
    audio_storage_path: Optional[str] = None
    generated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
