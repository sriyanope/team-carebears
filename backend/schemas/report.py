from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class ReportGenerateRequest(BaseModel):
    start_date: date
    end_date: date
    language: str = "en"
    patient_id: Optional[str] = None
    caregiver_name: Optional[str] = None
    patient_name: Optional[str] = None


class ReportReferenceResponse(BaseModel):
    date_label: str
    source_type: str


class ReportSummaryBulletResponse(BaseModel):
    text: str
    references: List[ReportReferenceResponse] = Field(default_factory=list)


class ReportFlagResponse(BaseModel):
    what: str
    why: str


class ReportSummaryResponse(BaseModel):
    id: str
    title: str
    start_date: date
    end_date: date
    generated_at: datetime


class ReportDetailResponse(BaseModel):
    id: str
    title: str
    start_date: date
    end_date: date
    summary_narrative: str = ""
    summary_bullets: List[ReportSummaryBulletResponse] = Field(default_factory=list)
    flags: List[ReportFlagResponse] = Field(default_factory=list)
    language: str = "en"
    audio_storage_path: Optional[str] = None
    generated_at: datetime
