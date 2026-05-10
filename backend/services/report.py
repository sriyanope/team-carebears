import json
import os
import re
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException

from ..config import settings
from ..firebase_client import get_firestore_client, normalize_timestamp
from ..models.patient import Patient
from ..models.report import Report, ReportFlag
from ..repositories import daily_wellbeing as daily_wellbeing_repo
from ..repositories import medication as medication_repo
from ..repositories import patient as patient_repo
from ..repositories import report as report_repo
from ..repositories import voice_note as voice_note_repo
from . import mock_data

REPORT_PROMPT = """
You are a caregiving report assistant. A family caregiver of a person with dementia has been logging observations over a period of time. Below is the evidence bundle containing all their logged data.

Your task:
1. Internally analyse the data across these categories: cognition changes, mood and behaviour changes, sleep/appetite/wellbeing patterns, and medication adherence. Do NOT output these as separate sections.
2. Write a SINGLE narrative paragraph that weaves together all the key findings from the period. The paragraph should:
   - Be written in plain, compassionate language that a caregiver can easily read and understand
   - Reference specific dates when describing incidents or changes (e.g. "On 5 May, he got lost..." not "he got lost once")
   - Mention patterns and trends, not just individual events
   - Be concise but comprehensive — aim for 4-8 sentences
   - NOT make clinical diagnoses or assign severity scores
   - Be grounded only in the data provided — do not infer or assume anything not in the evidence
3. Separately, produce a "Things to Flag" list — a flat list of specific items the caregiver should remember to mention to the doctor at their next visit. Each flag should be 1-2 sentences, referencing specific dates. These are plain observations, NOT clinical assessments. Only flag genuinely notable items — do not flag routine or expected things.

Respond ONLY with valid JSON in this exact format, no markdown fences, no preamble:
{{
  "summary": "Your single narrative paragraph here.",
  "flags": [
    {{"text": "Flag text referencing specific date(s)."}},
    {{"text": "Another flag."}}
  ]
}}

If there is very little data or nothing notable, still provide a brief summary stating that and return an empty flags array.

=== EVIDENCE BUNDLE ===
{evidence_bundle}
""".strip()

STRICT_JSON_SUFFIX = """

IMPORTANT:
- Return a single valid JSON object only.
- No markdown fences.
- No explanatory text before or after the JSON.
- Every flag item must be an object with a single "text" field.
""".rstrip()

DEFAULT_REPORT_MODEL_CANDIDATES = [
    "claude-sonnet-4-6",
    "claude-sonnet-4-5-20250929",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-opus-4-1-20250805",
]

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


def _format_date(value: date) -> str:
    return f"{value.day} {value.strftime('%b %Y')}"


def _format_time(value: datetime | None) -> str:
    if value is None:
        return "Unknown time"
    return value.astimezone(timezone.utc).strftime("%-I:%M %p UTC")


def _collect_text(response) -> str:
    parts: list[str] = []
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def _strip_json_fences(raw_text: str) -> str:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _parse_report_payload(raw_text: str) -> dict:
    cleaned = _strip_json_fences(raw_text)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("Claude response was not a JSON object")
    summary = data.get("summary")
    flags = data.get("flags", [])
    if not isinstance(summary, str):
        raise ValueError("Claude response did not include a string summary")
    if not isinstance(flags, list):
        raise ValueError("Claude response did not include a list of flags")
    return data


def _get_report_model_candidates() -> list[str]:
    configured = os.getenv("ANTHROPIC_REPORT_MODELS", "").strip()
    if not configured:
        return DEFAULT_REPORT_MODEL_CANDIDATES

    models = [item.strip() for item in configured.split(",") if item.strip()]
    return models or DEFAULT_REPORT_MODEL_CANDIDATES


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


def _mock_report(start_date: date, end_date: date) -> Report:
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
            summary="No notable caregiving data was recorded for this period.",
            flags=[],
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
        summary=source.summary,
        flags=[ReportFlag(severity="flag", text=flag.text) for flag in source.flags],
        generated_at=generated_at,
        created_at=generated_at,
        updated_at=generated_at,
    )


async def generate_report(patient_id: str, start_date: date, end_date: date) -> Report:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be on or before end_date")

    if mock_data.is_enabled():
        return _mock_report(start_date, end_date)

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

    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=502, detail="Anthropic API key is not configured")

    try:
        import anthropic
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=502, detail="Anthropic SDK is not installed") from exc

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    prompts = [
        REPORT_PROMPT.format(evidence_bundle=evidence_bundle),
        REPORT_PROMPT.format(evidence_bundle=evidence_bundle) + STRICT_JSON_SUFFIX,
    ]

    parsed_response: dict | None = None
    last_error: Exception | None = None
    api_error: Exception | None = None

    report_model_candidates = _get_report_model_candidates()

    for model_name in report_model_candidates:
        for prompt in prompts:
            try:
                response = client.messages.create(
                    model=model_name,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )
                parsed_response = _parse_report_payload(_collect_text(response))
                break
            except json.JSONDecodeError as exc:
                last_error = exc
            except ValueError as exc:
                last_error = exc
            except Exception as exc:
                api_error = exc
                if "404" in str(exc):
                    break
                raise HTTPException(status_code=502, detail=f"Claude API call failed: {exc}") from exc
        if parsed_response is not None:
            break

    if parsed_response is None:
        if api_error is not None and "404" in str(api_error):
            raise HTTPException(
                status_code=502,
                detail=(
                    "Claude API rejected all configured report models. "
                    f"Tried: {', '.join(report_model_candidates)}. Last error: {api_error}"
                ),
            ) from api_error
        message = f"Claude response could not be parsed as JSON: {last_error}" if last_error else "Claude response could not be parsed as JSON"
        raise HTTPException(status_code=502, detail=message)

    report_count = report_repo.count(patient_id)
    flags = [
        ReportFlag(severity="flag", text=item["text"])
        for item in parsed_response.get("flags", [])
        if isinstance(item, dict) and isinstance(item.get("text"), str) and item["text"].strip()
    ]

    report = Report(
        patient_id=patient_id,
        title=f"Report #{report_count + 1}",
        start_date=start_date,
        end_date=end_date,
        summary=parsed_response["summary"].strip(),
        flags=flags,
        generated_at=datetime.now(timezone.utc),
    )
    return report_repo.create(report)
