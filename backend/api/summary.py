from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.dashboard import SummaryResponse
from ..services import summary as summary_service

router = APIRouter()


@router.get("/api/summary", response_model=SummaryResponse)
def get_summary(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    d = target_date or date.today()
    return summary_service.get_summary(db, d)
