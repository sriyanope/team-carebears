from sqlalchemy.orm import Session
from ..models.patient import Patient


def get_first(db: Session) -> Patient | None:
    return db.query(Patient).first()


def create(db: Session, name: str, caregiver_name: str) -> Patient:
    patient = Patient(name=name, caregiver_name=caregiver_name)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
