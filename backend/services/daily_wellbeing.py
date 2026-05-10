from datetime import date

from ..models.daily_wellbeing import DailyWellbeing
from ..repositories import daily_wellbeing as daily_wellbeing_repo
from ..repositories import voice_note as voice_note_repo


def _attach_voice_note_transcript(entry: DailyWellbeing) -> DailyWellbeing:
    if not entry.voice_note_id:
        entry.voice_note_transcript = None
        return entry
    note = voice_note_repo.get_by_id(entry.voice_note_id)
    entry.voice_note_transcript = note.transcript if note else None
    return entry


def create_entry(
    patient_id: str,
    sleep_pattern: str,
    appetite: str,
    mood: str,
    voice_note_id: str | None = None,
) -> DailyWellbeing:
    entry = DailyWellbeing(
        patient_id=patient_id,
        date=date.today(),
        sleep_pattern=sleep_pattern,
        appetite=appetite,
        mood=mood,
        voice_note_id=voice_note_id,
    )
    created_entry = daily_wellbeing_repo.create(entry)
    return _attach_voice_note_transcript(created_entry)


def get_entries_by_date(patient_id: str, target_date: date) -> list[DailyWellbeing]:
    entries = daily_wellbeing_repo.get_by_date(patient_id, target_date)
    return [_attach_voice_note_transcript(entry) for entry in entries]


def get_all_entries(patient_id: str) -> list[DailyWellbeing]:
    entries = daily_wellbeing_repo.get_all(patient_id)
    return [_attach_voice_note_transcript(entry) for entry in entries]
