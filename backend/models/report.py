from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class ReportFlag(BaseModel):
    severity: str  # "red" or "amber"
    text: str


class Report(BaseModel):
    id: Optional[str] = None  # Firestore document ID
    patient_id: str
    title: str
    start_date: date
    end_date: date
    summary: Optional[str] = None
    flags: List[ReportFlag] = []
    generated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
