from datetime import date

from ..models.daily_wellbeing import DailyWellbeing
from ..repositories import daily_wellbeing as daily_wellbeing_repo


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
    return daily_wellbeing_repo.create(entry)


def get_entries_by_date(patient_id: str, target_date: date) -> list[DailyWellbeing]:
    return daily_wellbeing_repo.get_by_date(patient_id, target_date)


def get_all_entries(patient_id: str) -> list[DailyWellbeing]:
    return daily_wellbeing_repo.get_all(patient_id)
