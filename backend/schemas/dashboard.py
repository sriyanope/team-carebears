from typing import Optional
from pydantic import BaseModel
from .voice_note import VoiceNoteResponse


class ScheduleSlot(BaseModel):
    slot: str
    label: str
    status: str  # "done" | "current" | "upcoming"


class PatientInfo(BaseModel):
    name: str
    caregiver_name: str
    tracking_days: int


class DashboardMetrics(BaseModel):
    meds_done: int
    meds_total: int
    food_avg: int
    hydration: int
    notes_count: int


class DashboardResponse(BaseModel):
    patient: PatientInfo
    metrics: DashboardMetrics
    schedule: list[ScheduleSlot]
    recent_notes: list[VoiceNoteResponse]


class Flag(BaseModel):
    severity: str  # "red" | "amber"
    text: str
    sources: list[str]


class SummaryResponse(BaseModel):
    summary: str
    generated_at: str
    flags: list[Flag]
    questions: list[str]
