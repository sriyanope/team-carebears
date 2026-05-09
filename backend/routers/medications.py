from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import medication as med_service
from ..schemas.medication import MedicationResponse, MedicationUpdate

router = APIRouter()


@router.get("/api/medications", response_model=list[MedicationResponse])
def list_medications(db: Session = Depends(get_db)):
    return med_service.get_all(db)


@router.patch("/api/medications/{med_id}", response_model=MedicationResponse)
def update_medication(med_id: str, update: MedicationUpdate, db: Session = Depends(get_db)):
    med = med_service.update(db, med_id, update.done, update.voice_note)
    if med is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med
