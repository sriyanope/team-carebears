import json
from typing import Any

from ..config import settings
from ..schemas.daily_wellbeing import DailyWellbeingResponse
from ..schemas.medication import MedicationResponse
from ..schemas.onboarding import OnboardingResponse
from ..schemas.report import ReportDetailResponse
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


def get_voice_notes() -> list[VoiceNoteResponse] | None:
    data = _load_mock_data().get("voice_notes")
    if not data:
        return None
    return [VoiceNoteResponse.model_validate(item) for item in data]


def get_onboarding() -> OnboardingResponse | None:
    data = _load_mock_data().get("onboarding")
    if not data:
        return None
    return OnboardingResponse.model_validate(data)


def get_medications() -> list[MedicationResponse] | None:
    data = _load_mock_data().get("medications")
    if not data:
        return None
    return [MedicationResponse.model_validate(item) for item in data]


def get_daily_wellbeing() -> list[DailyWellbeingResponse] | None:
    data = _load_mock_data().get("daily_wellbeing")
    if not data:
        return None
    return [DailyWellbeingResponse.model_validate(item) for item in data]


def get_reports() -> list[ReportDetailResponse] | None:
    data = _load_mock_data().get("reports")
    if not data:
        return None
    normalized_reports = []
    for item in data:
        if not isinstance(item, dict):
            continue
        summary_narrative = item.get("summary_narrative") or item.get("summary") or ""
        summary_bullets = item.get("summary_bullets")
        if not isinstance(summary_bullets, list):
            summary_bullets = [{"text": summary_narrative, "references": []}] if summary_narrative else []

        flags = item.get("flags")
        if not isinstance(flags, list):
            flags = []
        normalized_flags = []
        for flag in flags:
            if not isinstance(flag, dict):
                continue
            if isinstance(flag.get("what"), str) and isinstance(flag.get("why"), str):
                normalized_flags.append(flag)
            elif isinstance(flag.get("text"), str):
                normalized_flags.append(
                    {
                        "what": flag["text"],
                        "why": "Mention this observation during the next doctor visit.",
                    }
                )

        normalized_reports.append(
            ReportDetailResponse.model_validate(
                {
                    **item,
                    "summary_narrative": summary_narrative,
                    "summary_bullets": summary_bullets,
                    "flags": normalized_flags,
                    "language": item.get("language", "en"),
                    "audio_storage_path": item.get("audio_storage_path"),
                }
            )
        )
    return normalized_reports


def get_report(report_id: str) -> ReportDetailResponse | None:
    reports = get_reports() or []
    for report in reports:
        if report.id == report_id:
            return report
    return None
