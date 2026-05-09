from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class ReportGenerateRequest(BaseModel):
    start_date: date
    end_date: date


class ReportFlagResponse(BaseModel):
    severity: str
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
