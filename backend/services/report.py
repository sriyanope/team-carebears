import json
import logging
import re
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.patient import Patient
from ..models.report import Report, ReportFlag, ReportReference, ReportSummaryBullet
from ..repositories import daily_wellbeing as daily_wellbeing_repo
from ..repositories import medication as medication_repo
from ..repositories import patient as patient_repo
from ..repositories import report as report_repo
from ..repositories import voice_note as voice_note_repo
from . import mock_data

logger = logging.getLogger(__name__)

REPORT_PROMPT_TEMPLATE = """
You are a caregiving report assistant. A family caregiver of a person with dementia has been logging observations over a period of time. Below is the evidence bundle containing all their logged data.

Generate the report content in {language_name}.

Your task:
1. Internally analyze the data across these categories: cognition changes, mood and behaviour changes, sleep/appetite/wellbeing patterns, and medication adherence. Do NOT output these as separate sections.
2. Write a narrative summary paragraph in {language_name}. This must be the richer, detailed version of the summary. It should:
   - Be written in plain, compassionate language that a caregiver can easily read and understand
   - Reference specific dates when describing incidents or changes
   - Mention patterns and trends, not just isolated incidents
   - Be concise but still detailed enough to preserve important context
   - NOT make clinical diagnoses or assign severity scores
   - Be grounded only in the data provided
3. Write a condensed bullet-point summary in {language_name}. These bullets must:
   - Cover the same key findings as the narrative summary
   - Stay information-dense and not be watered down
   - Include compact references for each bullet
   - Use references as objects in the form {{"date_label": "5 May", "source_type": "voice_note"}} where source_type is one of: "voice_note", "daily_wellbeing", "medication"
4. Separately, produce a "Things to Flag" list in {language_name}. Each flag must contain:
   - "what": what happened
   - "why": why the caregiver should mention it to the doctor
   Only include genuinely notable items.

Respond ONLY with valid JSON in this exact format, no markdown fences, no preamble:
{{
  "summary_narrative": "Detailed narrative summary paragraph.",
  "summary_bullets": [
    {{
      "text": "Condensed but detailed summary point.",
      "references": [
        {{"date_label": "5 May", "source_type": "voice_note"}}
      ]
    }}
  ],
  "flags": [
    {{
      "what": "What happened.",
      "why": "Why it should be flagged."
    }}
  ]
}}

If there is very little data or nothing notable:
- still provide a brief narrative summary
- still provide at least one summary bullet
- return an empty flags array if nothing needs to be flagged

=== EVIDENCE BUNDLE ===
{evidence_bundle}
""".strip()

REPORT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary_narrative": {
            "type": "string",
            "description": "A detailed, compassionate narrative summary paragraph grounded only in the evidence bundle.",
        },
        "summary_bullets": {
            "type": "array",
            "description": "Condensed but information-dense summary bullets with compact evidence references.",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "references": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date_label": {"type": "string"},
                                "source_type": {
                                    "type": "string",
                                    "enum": ["voice_note", "daily_wellbeing", "medication"],
                                },
                            },
                            "required": ["date_label", "source_type"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["text", "references"],
                "additionalProperties": False,
            },
        },
        "flags": {
            "type": "array",
            "description": "Genuinely notable items the caregiver should mention to the doctor.",
            "items": {
                "type": "object",
                "properties": {
                    "what": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": ["what", "why"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary_narrative", "summary_bullets", "flags"],
    "additionalProperties": False,
}

REPORT_LANGUAGE_NAMES = {
    "en": "English",
    "zh": "Chinese",
    "ms": "Malay",
    "ta": "Tamil",
}

SLEEP_LABELS = {
    "earlier_sleep_later_wake": "Earlier sleep time, later wake time",
    "same": "No change",
    "later_sleep_earlier_wake": "Later sleep time, earlier wake time",
}

APPETITE_LABELS = {
    "eating_less": "Eating less than usual",
    "same": "No change",
    "eating_more": "Eating more than usual",
}

MOOD_LABELS = {
    "happy": "Happy",
    "ok": "OK",
    "neutral": "Neutral",
    "sad": "Sad",
    "upset": "Upset",
}

VALID_SOURCE_TYPES = {"voice_note", "daily_wellbeing", "medication"}


def _format_date(value: date) -> str:
    return f"{value.day} {value.strftime('%b %Y')}"


def _format_time(value: datetime | None) -> str:
    if value is None:
        return "Unknown time"
    return value.astimezone(timezone.utc).strftime("%-I:%M %p UTC")


def _normalize_report_language(language: str | None) -> str:
    normalized = (language or "en").strip().lower()
    return normalized if normalized in REPORT_LANGUAGE_NAMES else "en"


def _report_language_name(language: str) -> str:
    return REPORT_LANGUAGE_NAMES.get(_normalize_report_language(language), "English")


def _collect_response_text(response) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    parts: list[str] = []
    for output_item in getattr(response, "output", []) or []:
        for content_item in getattr(output_item, "content", []) or []:
            text = getattr(content_item, "text", None)
            if isinstance(text, str) and text:
                parts.append(text)
    return "\n".join(parts).strip()


def _strip_json_fences(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _parse_references(raw_references: object) -> list[dict]:
    if not isinstance(raw_references, list):
        return []
    normalized: list[dict] = []
    for item in raw_references:
        if not isinstance(item, dict):
            continue
        date_label = item.get("date_label")
        source_type = item.get("source_type")
        if not isinstance(date_label, str) or not date_label.strip():
            continue
        if not isinstance(source_type, str):
            continue
        normalized_source_type = source_type.strip().lower()
        if normalized_source_type not in VALID_SOURCE_TYPES:
            continue
        normalized.append(
            {
                "date_label": date_label.strip(),
                "source_type": normalized_source_type,
            }
        )
    return normalized


def _parse_report_payload(raw_text: str) -> dict:
    cleaned = _strip_json_fences(raw_text)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("OpenAI report response was not a JSON object")

    summary_narrative = data.get("summary_narrative")
    summary_bullets = data.get("summary_bullets", [])
    flags = data.get("flags", [])

    if not isinstance(summary_narrative, str) or not summary_narrative.strip():
        raise ValueError("OpenAI report response did not include a string summary_narrative")
    if not isinstance(summary_bullets, list):
        raise ValueError("OpenAI report response did not include a list summary_bullets")
    if not isinstance(flags, list):
        raise ValueError("OpenAI report response did not include a list flags")

    normalized_bullets: list[dict] = []
    for item in summary_bullets:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        normalized_bullets.append(
            {
                "text": text.strip(),
                "references": _parse_references(item.get("references", [])),
            }
        )

    if not normalized_bullets:
        raise ValueError("OpenAI report response did not include any valid summary bullets")

    normalized_flags: list[dict] = []
    for item in flags:
        if not isinstance(item, dict):
            continue
        what = item.get("what")
        why = item.get("why")
        if not isinstance(what, str) or not what.strip():
            continue
        if not isinstance(why, str) or not why.strip():
            continue
        normalized_flags.append({"what": what.strip(), "why": why.strip()})

    return {
        "summary_narrative": summary_narrative.strip(),
        "summary_bullets": normalized_bullets,
        "flags": normalized_flags,
    }


def _load_patient_by_id(patient_id: str) -> Patient | None:
    if settings.FIREBASE_MODE:
        client = get_firestore_client()
        doc = client.collection("patients").document(patient_id).get()
        if not doc.exists:
            return None

        data = doc.to_dict() or {}
        caregiver_name = data.get("caregiver_name")
        if caregiver_name is None and isinstance(data.get("caregiver"), dict):
            caregiver_name = data["caregiver"].get("name")

        patient_name = data.get("name")
        if patient_name is None and isinstance(data.get("patient"), dict):
            patient_name = data["patient"].get("name")

        return Patient(
            id=doc.id,
            name=patient_name or "",
            caregiver_name=caregiver_name or "",
            created_at=normalize_timestamp(data.get("created_at")),
            updated_at=normalize_timestamp(data.get("updated_at")),
        )

    patient = patient_repo.get_first(None)
    if patient is None or patient.id != patient_id:
        return None
    return patient


def _daterange(start_date: date, end_date: date) -> list[date]:
    days: list[date] = []
    current = start_date
    while current <= end_date:
        days.append(current)
        current += timedelta(days=1)
    return days


def _build_medication_summary(medications: list, voice_notes: list, start_date: date, end_date: date) -> list[str]:
    rows: list[str] = []
    all_days = _daterange(start_date, end_date)

    for medication in medications:
        created_day = medication.created_at.date() if medication.created_at else start_date
        active_days = [day for day in all_days if day >= created_day]
        if not active_days:
            continue

        known_taken_days = set()
        if medication.created_at:
            created_at_day = medication.created_at.date()
            if start_date <= created_at_day <= end_date:
                known_taken_days.add(created_at_day)
        if medication.updated_at:
            updated_at_day = medication.updated_at.date()
            if start_date <= updated_at_day <= end_date:
                known_taken_days.add(updated_at_day)

        linked_notes = [
            note for note in voice_notes
            if note.med_id == medication.id and note.created_at is not None
        ]
        for note in linked_notes:
            note_day = note.created_at.date()
            if start_date <= note_day <= end_date:
                known_taken_days.add(note_day)

        taken_days = sorted(day for day in active_days if day in known_taken_days)
        missed_days = sorted(day for day in active_days if day not in known_taken_days)

        taken_text = ", ".join(_format_date(day) for day in taken_days) if taken_days else "None recorded"
        missed_text = ", ".join(_format_date(day) for day in missed_days) if missed_days else "None recorded"
        note_text = medication.note or "No note"
        rows.append(
            f"{medication.name} ({note_text}): Taken on {taken_text}; Missed on {missed_text}"
        )

    return rows


def _build_evidence_bundle(patient_name: str, start_date: date, end_date: date, voice_notes: list, wellbeing_entries: list, medications: list) -> str:
    lines = [
        "=== CAREGIVING EVIDENCE BUNDLE ===",
        f"Patient: {patient_name}",
        f"Date Range: {start_date.isoformat()} to {end_date.isoformat()}",
        "",
        "--- VOICE NOTE TRANSCRIPTS ---",
    ]

    if voice_notes:
        for note in sorted(voice_notes, key=lambda item: item.created_at or datetime.min.replace(tzinfo=timezone.utc)):
            note_date = note.created_at.date() if note.created_at else start_date
            note_time = _format_time(note.created_at)
            lines.append(f"[{_format_date(note_date)} {note_time}] ({note.note_type}): {note.transcript}")
    else:
        lines.append("No entries recorded for this period.")

    lines.extend(["", "--- DAILY WELLBEING ENTRIES ---"])
    if wellbeing_entries:
        for entry in sorted(wellbeing_entries, key=lambda item: item.date):
            lines.append(
                f"[{_format_date(entry.date)}]: Sleep: {SLEEP_LABELS.get(entry.sleep_pattern, entry.sleep_pattern)} | "
                f"Appetite: {APPETITE_LABELS.get(entry.appetite, entry.appetite)} | "
                f"Mood: {MOOD_LABELS.get(entry.mood, entry.mood)}"
            )
    else:
        lines.append("No entries recorded for this period.")

    lines.extend(["", "--- MEDICATION LOGS ---"])
    medication_rows = _build_medication_summary(medications, voice_notes, start_date, end_date)
    if medication_rows:
        lines.extend(medication_rows)
    else:
        lines.append("No entries recorded for this period.")

    return "\n".join(lines)


def _build_report_prompt(evidence_bundle: str, language: str) -> str:
    return REPORT_PROMPT_TEMPLATE.format(
        evidence_bundle=evidence_bundle,
        language_name=_report_language_name(language),
    )


def _report_from_payload(
    patient_id: str,
    title: str,
    start_date: date,
    end_date: date,
    language: str,
    payload: dict,
) -> Report:
    return Report(
        patient_id=patient_id,
        title=title,
        start_date=start_date,
        end_date=end_date,
        summary_narrative=payload["summary_narrative"],
        summary_bullets=[
            ReportSummaryBullet(
                text=item["text"],
                references=[
                    ReportReference(
                        date_label=reference["date_label"],
                        source_type=reference["source_type"],
                    )
                    for reference in item.get("references", [])
                ],
            )
            for item in payload["summary_bullets"]
        ],
        flags=[
            ReportFlag(what=item["what"], why=item["why"])
            for item in payload["flags"]
        ],
        language=_normalize_report_language(language),
        generated_at=datetime.now(timezone.utc),
    )


def _mock_report(start_date: date, end_date: date, language: str = "en") -> Report:
    reports = mock_data.get_reports() or []
    source = reports[0] if reports else None
    generated_at = datetime.now(timezone.utc)
    if source is None:
        return Report(
            id="mock-report-generated",
            patient_id="mock-patient",
            title="Report #1",
            start_date=start_date,
            end_date=end_date,
            summary_narrative="No notable caregiving data was recorded for this period.",
            summary_bullets=[
                ReportSummaryBullet(
                    text="No notable caregiving data was recorded for this period.",
                    references=[],
                )
            ],
            flags=[],
            language=_normalize_report_language(language),
            audio_storage_path=None,
            generated_at=generated_at,
            created_at=generated_at,
            updated_at=generated_at,
        )

    return Report(
        id=source.id,
        patient_id="mock-patient",
        title=source.title,
        start_date=start_date,
        end_date=end_date,
        summary_narrative=source.summary_narrative,
        summary_bullets=[
            ReportSummaryBullet(
                text=item.text,
                references=[
                    ReportReference(date_label=reference.date_label, source_type=reference.source_type)
                    for reference in item.references
                ],
            )
            for item in source.summary_bullets
        ],
        flags=[
            ReportFlag(what=item.what, why=item.why)
            for item in source.flags
        ],
        language=source.language or _normalize_report_language(language),
        audio_storage_path=source.audio_storage_path,
        generated_at=generated_at,
        created_at=generated_at,
        updated_at=generated_at,
    )


def get_report_audio_bytes(report: Report) -> bytes:
    raise HTTPException(status_code=404, detail="Report audio overview is currently disabled")


def get_report_detail(report_id: str) -> Report | None:
    return report_repo.get_by_id(report_id)


async def generate_report(patient_id: str, start_date: date, end_date: date, language: str = "en") -> Report:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")

    normalized_language = _normalize_report_language(language)

    if mock_data.is_enabled():
        return _mock_report(start_date, end_date, normalized_language)

    patient = _load_patient_by_id(patient_id)
    if patient is None or not patient.id:
        raise HTTPException(status_code=404, detail="No patient found")

    try:
        voice_notes = voice_note_repo.get_by_date_range(patient_id, start_date, end_date)
        wellbeing_entries = daily_wellbeing_repo.get_by_date_range(patient_id, start_date, end_date)
        medications = [
            medication
            for medication in medication_repo.get_all(None)
            if medication.patient_id == patient_id
            and (medication.created_at is None or medication.created_at.date() <= end_date)
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to gather report evidence: {exc}") from exc

    evidence_bundle = _build_evidence_bundle(
        patient_name=patient.name,
        start_date=start_date,
        end_date=end_date,
        voice_notes=voice_notes,
        wellbeing_entries=wellbeing_entries,
        medications=medications,
    )

    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=502, detail="OpenAI API key is not configured")

    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=502, detail="OpenAI SDK is not installed") from exc

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = _build_report_prompt(evidence_bundle, normalized_language)

    try:
        response = client.responses.create(
            model=settings.OPENAI_REPORT_MODEL,
            input=prompt,
            max_output_tokens=2400,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "caregiving_report",
                    "strict": True,
                    "schema": REPORT_RESPONSE_SCHEMA,
                }
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI report generation failed: {exc}") from exc

    try:
        parsed_response = _parse_report_payload(_collect_response_text(response))
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI report response could not be parsed as JSON: {exc}",
        ) from exc

    report_count = report_repo.count(patient_id)
    report = _report_from_payload(
        patient_id=patient_id,
        title=f"Report #{report_count + 1}",
        start_date=start_date,
        end_date=end_date,
        language=normalized_language,
        payload=parsed_response,
    )
    return report_repo.create(report)
