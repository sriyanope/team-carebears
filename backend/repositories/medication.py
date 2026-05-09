from sqlalchemy.orm import Session
from ..models.medication import Medication


def get_all(db: Session) -> list[Medication]:
    return db.query(Medication).order_by(Medication.time_str.asc()).all()


def get_by_patient(db: Session, patient_id: str) -> list[Medication]:
    return (
        db.query(Medication)
        .filter(Medication.patient_id == patient_id)
        .order_by(Medication.time_str.asc())
        .all()
    )


def get_by_id(db: Session, med_id: str) -> Medication | None:
    return db.query(Medication).filter(Medication.id == med_id).first()


def update(db: Session, med: Medication, done: bool, voice_note_text: str | None = None) -> Medication:
    med.done = done
    if voice_note_text is not None:
        med.voice_note_text = voice_note_text
    db.commit()
    db.refresh(med)
    return med


def create(
    db: Session,
    patient_id: str,
    name: str,
    note: str | None,
    time_str: str,
    done: bool = False,
    voice_note_text: str | None = None,
) -> Medication:
    med = Medication(
        patient_id=patient_id,
        name=name,
        note=note,
        time_str=time_str,
        done=done,
        voice_note_text=voice_note_text,
    )
    db.add(med)
    return med
