from datetime import date
from sqlalchemy.orm import Session
from ..repositories import daily_log as log_repo, patient as patient_repo
from ..schemas.daily_log import TrackerCreate, FoodData, HydrationUpdate


def get_by_date(db: Session, target_date: date) -> object | None:
    patient = patient_repo.get_first(db)
    if not patient:
        return None
    return log_repo.get_by_date(db, patient.id, target_date)


def save_tracker(db: Session, data: TrackerCreate) -> object:
    patient = patient_repo.get_first(db)
    today = date.today()
    fields: dict = {}
    if data.mood is not None:
        fields["mood"] = data.mood
    if data.food:
        if data.food.breakfast is not None:
            fields["food_breakfast"] = data.food.breakfast
        if data.food.lunch is not None:
            fields["food_lunch"] = data.food.lunch
        if data.food.dinner is not None:
            fields["food_dinner"] = data.food.dinner
    if data.hydration is not None:
        fields["hydration"] = data.hydration
    if data.dementia_signs:
        ds = data.dementia_signs
        fields.update({
            "confusion": ds.confusion,
            "agitation": ds.agitation,
            "wandering": ds.wandering,
            "recognition": ds.recognition,
            "hallucinations": ds.hallucinations,
            "sleep_disruptions": ds.sleep_disruptions,
        })
    return log_repo.upsert(db, patient_id=patient.id, target_date=today, **fields)


def update_food(db: Session, food: FoodData) -> object:
    patient = patient_repo.get_first(db)
    fields = {}
    if food.breakfast is not None:
        fields["food_breakfast"] = food.breakfast
    if food.lunch is not None:
        fields["food_lunch"] = food.lunch
    if food.dinner is not None:
        fields["food_dinner"] = food.dinner
    return log_repo.upsert(db, patient_id=patient.id, target_date=date.today(), **fields)


def update_hydration(db: Session, update: HydrationUpdate) -> object:
    patient = patient_repo.get_first(db)
    return log_repo.upsert(
        db, patient_id=patient.id, target_date=date.today(), hydration=update.glasses
    )
