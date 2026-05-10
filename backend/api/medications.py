from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.medication import (
    MedicationCreate,
    MedicationDetailsUpdate,
    MedicationResponse,
    MedicationUpdate,
)
from ..services import medication as med_service
from ..services import mock_data

router = APIRouter()


@router.get("/api/medications", response_model=list[MedicationResponse])
def list_medications(patient_id: str | None = None, db: Session = Depends(get_db)):
    if mock_data.is_enabled():
        return med_service.get_all(db, patient_id or "")
    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id is required")
    return med_service.get_all(db, patient_id)


@router.post("/api/medications", response_model=MedicationResponse)
def create_medication(payload: MedicationCreate, db: Session = Depends(get_db)):
    med = med_service.create(db, payload)
    if med is None:
        raise HTTPException(status_code=400, detail="Create a patient profile before adding medications")
    return med


@router.get("/api/medications/{med_id}", response_model=MedicationResponse)
def get_medication(med_id: str, db: Session = Depends(get_db)):
    med = med_service.get_by_id(db, med_id)
    if med is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.patch("/api/medications/{med_id}", response_model=MedicationResponse)
def update_medication(med_id: str, update: MedicationUpdate, db: Session = Depends(get_db)):
    med = med_service.update(db, med_id, update.done, update.voice_note)
    if med is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.put("/api/medications/{med_id}", response_model=MedicationResponse)
def update_medication_details(
    med_id: str,
    payload: MedicationDetailsUpdate,
    db: Session = Depends(get_db),
):
    med = med_service.update_details(db, med_id, payload)
    if med is None:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.delete("/api/medications/{med_id}", status_code=204)
def delete_medication(med_id: str, db: Session = Depends(get_db)):
    deleted = med_service.delete(db, med_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Medication not found")
