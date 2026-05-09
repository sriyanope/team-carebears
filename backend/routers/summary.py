from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import summary as summary_service
from ..repositories import voice_note as vn_repo, medication as med_repo, daily_log as log_repo, patient as patient_repo
from ..schemas.dashboard import SummaryResponse

router = APIRouter()


@router.get("/api/summary", response_model=SummaryResponse)
def get_summary(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    d = target_date or date.today()
    patient = patient_repo.get_first(db)
    patient_id = patient.id if patient else ""
    notes = vn_repo.get_by_date_for_patient(db, patient_id, d) if patient else []
    meds = med_repo.get_by_patient(db, patient_id) if patient else []
    log = log_repo.get_by_date(db, patient_id, d)
    return summary_service.generate_summary(notes, meds, log, d)
