from datetime import date
from uuid import uuid4
from sqlalchemy.orm import Session
from ..models.daily_log import DailyLog


def get_by_date(db: Session, patient_id: str, target_date: date) -> DailyLog | None:
    return (
        db.query(DailyLog)
        .filter(DailyLog.patient_id == patient_id, DailyLog.date == target_date)
        .first()
    )


def upsert(db: Session, patient_id: str, target_date: date, **fields) -> DailyLog:
    log = get_by_date(db, patient_id, target_date)
    if log is None:
        log = DailyLog(id=str(uuid4()), patient_id=patient_id, date=target_date)
        db.add(log)
    for key, value in fields.items():
        if value is not None:
            setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log
