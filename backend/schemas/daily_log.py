from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class FoodData(BaseModel):
    breakfast: Optional[int] = None
    lunch: Optional[int] = None
    dinner: Optional[int] = None


class HydrationUpdate(BaseModel):
    glasses: int


class DementiaSignsData(BaseModel):
    confusion: str = "None"
    agitation: str = "None"
    wandering: str = "No"
    recognition: str = "Normal"
    hallucinations: str = "None"
    sleep_disruptions: int = 0


class TrackerCreate(BaseModel):
    mood: Optional[int] = None
    food: Optional[FoodData] = None
    hydration: Optional[int] = None
    dementia_signs: Optional[DementiaSignsData] = None


class DailyLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    date: date
    mood: Optional[int]
    food_breakfast: int
    food_lunch: int
    food_dinner: int
    hydration: int
    confusion: str
    agitation: str
    wandering: str
    recognition: str
    hallucinations: str
    sleep_disruptions: int
    created_at: datetime
    updated_at: datetime
