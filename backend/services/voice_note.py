import logging
import os
import tempfile
from datetime import date

from fastapi import UploadFile
from sqlalchemy.orm import Session

from . import categorisation as categorisation_service
from . import mock_data
from . import transcription as transcription_service
from ..repositories import patient as patient_repo
from ..repositories import voice_note as vn_repo

logger = logging.getLogger(__name__)


async def create_from_audio(
    db: Session,
    audio: UploadFile,
    note_type: str,
    slot: str | None,
    med_id: str | None,
) -> object | None:
    if mock_data.is_enabled():
        notes = mock_data.get_voice_notes() or []
        return notes[0] if notes else None
    patient = patient_repo.get_first(db)
    if not patient:
        return None
    suffix = "." + (audio.filename or "audio.webm").rsplit(".", 1)[-1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
        content = await audio.read()
        tmp.write(content)

    try:
        transcript = transcription_service.transcribe(tmp_path)
        logger.info("Voice note transcript: %s", transcript)
        result = categorisation_service.categorise(transcript)
    finally:
        os.unlink(tmp_path)

    return vn_repo.create(
        db,
        patient_id=patient.id,
        transcript=transcript,
        categories=result.get("categories", []),
        ai_tags=result.get("ai_tags", []),
        severity=result.get("severity", "low"),
        note_type=note_type,
        slot=slot,
        med_id=med_id,
    )


def get_by_date(db: Session, target_date: date) -> list:
    if mock_data.is_enabled():
        return mock_data.get_voice_notes() or []
    patient = patient_repo.get_first(db)
    if not patient:
        return []
    return vn_repo.get_by_date_for_patient(db, patient.id, target_date)
