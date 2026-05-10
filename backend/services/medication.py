from sqlalchemy.orm import Session

from . import mock_data
from ..repositories import medication as med_repo
from ..repositories import patient as patient_repo
from ..schemas.medication import MedicationCreate, MedicationDetailsUpdate


def _build_note(
    *,
    dosage: str | None,
    frequency_per_week: int | None,
    special_instructions: str | None,
    expiry_date,
) -> str | None:
    note_parts = []
    if dosage:
        note_parts.append(f"Dosage: {dosage}")
    if frequency_per_week:
        note_parts.append(f"{frequency_per_week} times/week")
    if special_instructions:
        note_parts.append(f"Instructions: {special_instructions}")
    if expiry_date:
        formatted_expiry = expiry_date.isoformat() if hasattr(expiry_date, "isoformat") else str(expiry_date)
        note_parts.append(f"Expires: {formatted_expiry}")
    return " | ".join(note_parts) if note_parts else None


def get_all(db: Session, patient_id: str) -> list:
    if mock_data.is_enabled():
        return mock_data.get_medications() or []
    patient = patient_repo.get_by_id(db, patient_id)
    if not patient:
        return []
    return med_repo.get_by_patient(db, patient.id)


def get_by_id(db: Session, med_id: str) -> object | None:
    if mock_data.is_enabled():
        meds = mock_data.get_medications() or []
        return next((med for med in meds if med.id == med_id), None)
    return med_repo.get_by_id(db, med_id)


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


def create(db: Session, payload: MedicationCreate) -> object | None:
    patient = patient_repo.get_first(db)
    if patient is None:
        return None

    return med_repo.create(
        db,
        patient_id=patient.id,
        name=payload.name,
        note=_build_note(
            dosage=payload.dosage,
            frequency_per_week=payload.frequency_per_week,
            special_instructions=payload.special_instructions,
            expiry_date=payload.expiry_date,
        ),
        time_str="09:00",
        dosage=payload.dosage,
        frequency_per_week=payload.frequency_per_week,
        special_instructions=payload.special_instructions,
        expiry_date=payload.expiry_date,
    )


def update_details(db: Session, med_id: str, payload: MedicationDetailsUpdate) -> object | None:
    med = get_by_id(db, med_id)
    if med is None:
        return None

    updates = payload.model_dump(exclude_unset=True)

    dosage = updates.get("dosage", getattr(med, "dosage", None))
    frequency_per_week = (
        updates["frequency_per_week"]
        if "frequency_per_week" in updates
        else getattr(med, "frequency_per_week", None)
    )
    special_instructions = (
        updates["special_instructions"]
        if "special_instructions" in updates
        else getattr(med, "special_instructions", None)
    )
    expiry_date = updates.get("expiry_date", getattr(med, "expiry_date", None))

    return med_repo.update_details(
        db,
        med,
        updates=updates,
        note=_build_note(
            dosage=dosage,
            frequency_per_week=frequency_per_week,
            special_instructions=special_instructions,
            expiry_date=expiry_date,
        ),
    )


def delete(db: Session, med_id: str) -> bool:
    med = get_by_id(db, med_id)
    if med is None:
        return False
    if mock_data.is_enabled():
        return True
    med_repo.delete(db, med)
    return True
