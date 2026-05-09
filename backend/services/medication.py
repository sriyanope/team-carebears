from sqlalchemy.orm import Session
from ..repositories import medication as med_repo, patient as patient_repo


def get_all(db: Session) -> list:
    patient = patient_repo.get_first(db)
    if not patient:
        return []
    return med_repo.get_by_patient(db, patient.id)


def update(db: Session, med_id: str, done: bool, voice_note: str | None = None) -> object | None:
    med = med_repo.get_by_id(db, med_id)
    if med is None:
        return None
    return med_repo.update(db, med, done=done, voice_note_text=voice_note)
