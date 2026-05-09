import logging
import os
import tempfile
from datetime import date

from fastapi import UploadFile

from . import mock_data
from . import transcription as transcription_service
from ..repositories import patient as patient_repo
from ..repositories import voice_note as vn_repo

logger = logging.getLogger(__name__)


async def create_from_audio(
    audio: UploadFile,
    note_type: str,
    language: str = "en",
    med_id: str | None = None,
) -> object | None:
    if mock_data.is_enabled():
        notes = mock_data.get_voice_notes() or []
        return notes[0] if notes else None
    patient = patient_repo.get_first(None)
    if not patient:
        return None
    suffix = "." + (audio.filename or "audio.webm").rsplit(".", 1)[-1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
        content = await audio.read()
        tmp.write(content)

    try:
        transcript = transcription_service.transcribe(tmp_path, language=language)
        logger.info("Voice note transcript: %s", transcript)
    finally:
        os.unlink(tmp_path)

    return vn_repo.create(
        patient_id=patient.id,
        transcript=transcript,
        note_type=note_type,
        language=language,
        med_id=med_id,
    )


def get_all() -> list:
    if mock_data.is_enabled():
        return mock_data.get_voice_notes() or []
    patient = patient_repo.get_first(None)
    if not patient:
        return []
    return vn_repo.get_all(patient.id)


def get_by_date(target_date: date) -> list:
    if mock_data.is_enabled():
        return mock_data.get_voice_notes() or []
    patient = patient_repo.get_first(None)
    if not patient:
        return []
    return vn_repo.get_by_date(patient.id, target_date)
