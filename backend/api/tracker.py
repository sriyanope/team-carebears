from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.daily_log import DailyLogResponse, FoodData, HydrationUpdate, TrackerCreate
from ..services import tracker as tracker_service

router = APIRouter()


@router.get("/api/tracker/{target_date}", response_model=DailyLogResponse)
def get_tracker(target_date: date, db: Session = Depends(get_db)):
    log = tracker_service.get_by_date(db, target_date)
    if log is None:
        raise HTTPException(status_code=404, detail="No log found")
    return log


@router.post("/api/tracker", response_model=DailyLogResponse)
def save_tracker(data: TrackerCreate, db: Session = Depends(get_db)):
    log = tracker_service.save_tracker(db, data)
    if log is None:
        raise HTTPException(status_code=404, detail="No patient found")
    return log


@router.patch("/api/food", response_model=DailyLogResponse)
def update_food(food: FoodData, db: Session = Depends(get_db)):
    log = tracker_service.update_food(db, food)
    if log is None:
        raise HTTPException(status_code=404, detail="No patient found")
    return log


@router.patch("/api/hydration", response_model=DailyLogResponse)
def update_hydration(update: HydrationUpdate, db: Session = Depends(get_db)):
    log = tracker_service.update_hydration(db, update)
    if log is None:
        raise HTTPException(status_code=404, detail="No patient found")
    return log
