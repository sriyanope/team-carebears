from sqlalchemy.orm import Session

from . import mock_data
from ..repositories import medication as med_repo
from ..repositories import patient as patient_repo


def get_all(db: Session) -> list:
    if mock_data.is_enabled():
        return mock_data.get_medications() or []
    patient = patient_repo.get_first(db)
    if not patient:
        return []
    print(patient.id)
    print(med_repo.get_by_patient(db, "/patients/"+patient.id))
    return med_repo.get_by_patient(db, patient.id)


def update(db: Session, med_id: str, done: bool, voice_note: str | None = None) -> object | None:
    if mock_data.is_enabled():
        meds = mock_data.get_medications() or []
        for med in meds:
            if med.id == med_id:
                return med
        return meds[0] if meds else None
    med = med_repo.get_by_id(db, med_id)
    if med is None:
        return None
    return med_repo.update(db, med, done=done, voice_note_text=voice_note)

