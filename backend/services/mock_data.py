import json
from typing import Any

from ..config import settings
from ..schemas.dashboard import DashboardResponse, SummaryResponse
from ..schemas.daily_log import DailyLogResponse
from ..schemas.medication import MedicationResponse
from ..schemas.voice_note import VoiceNoteResponse

_mock_cache: dict[str, Any] | None = None


def is_enabled() -> bool:
    return settings.MOCK_MODE


def _load_mock_data() -> dict[str, Any]:
    global _mock_cache
    if _mock_cache is not None:
        return _mock_cache
    raw = settings.MOCK_DATA_JSON.strip()
    if not raw:
        _mock_cache = {}
        return _mock_cache
    try:
        _mock_cache = json.loads(raw)
    except json.JSONDecodeError:
        _mock_cache = {}
    return _mock_cache


def get_dashboard() -> DashboardResponse | None:
    data = _load_mock_data().get("dashboard")
    if not data:
        return None
    return DashboardResponse.model_validate(data)


def get_voice_notes() -> list[VoiceNoteResponse] | None:
    data = _load_mock_data().get("voice_notes")
    if not data:
        return None
    return [VoiceNoteResponse.model_validate(item) for item in data]


def get_medications() -> list[MedicationResponse] | None:
    data = _load_mock_data().get("medications")
    if not data:
        return None
    return [MedicationResponse.model_validate(item) for item in data]


def get_daily_log() -> DailyLogResponse | None:
    data = _load_mock_data().get("daily_log")
    if not data:
        return None
    return DailyLogResponse.model_validate(data)


def get_summary() -> SummaryResponse | None:
    data = _load_mock_data().get("summary")
    if not data:
        return None
    return SummaryResponse.model_validate(data)
