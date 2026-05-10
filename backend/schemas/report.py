from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class ReportGenerateRequest(BaseModel):
    start_date: date
    end_date: date
    caregiver_name: Optional[str] = None
    patient_name: Optional[str] = None


class ReportFlagResponse(BaseModel):
    severity: str = "flag"
    text: str


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
    summary: str
    flags: List[ReportFlagResponse]
    generated_at: datetime
