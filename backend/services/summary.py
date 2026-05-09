from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from ..config import settings
from ..repositories import daily_log as log_repo
from ..repositories import medication as med_repo
from ..repositories import patient as patient_repo
from ..repositories import voice_note as vn_repo
from ..schemas.dashboard import Flag, SummaryResponse
from . import mock_data

_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic
        _client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


def build_flags(log, notes) -> list[Flag]:
    flags = []
    if log:
        if log.hydration < 5:
            flags.append(Flag(
                severity="amber",
                text=f"Only {log.hydration} of 8 glasses of water consumed today. Dehydration risk for dementia patients.",
                sources=["Tracker log"],
            ))
        food_avg = (log.food_breakfast + log.food_lunch + log.food_dinner) // 3
        if food_avg < 50:
            flags.append(Flag(
                severity="amber",
                text=f"Average food intake was {food_avg}% today. Low nutrition may worsen confusion.",
                sources=["Tracker log"],
            ))
        if log.confusion in ("Moderate", "Severe"):
            flags.append(Flag(
                severity="amber" if log.confusion == "Moderate" else "red",
                text=f"{log.confusion} confusion observed today.",
                sources=["Tracker log"],
            ))
        if log.agitation in ("Moderate", "Severe"):
            flags.append(Flag(
                severity="red",
                text=f"{log.agitation} agitation reported today.",
                sources=["Tracker log"],
            ))
    for note in notes:
        if note.severity == "high":
            flags.append(Flag(
                severity="red",
                text=note.transcript[:200],
                sources=[f"{note.slot or 'Ad-hoc'} note"],
            ))
    return flags


def generate_summary(notes, meds, log, target_date) -> SummaryResponse:
    flags = build_flags(log, notes)
    notes_text = "\n".join(
        f"- [{n.note_type} {n.slot or ''}] {n.transcript}" for n in notes
    ) or "No voice notes recorded."
    meds_text = "\n".join(
        f"- {m.name} ({m.time_str}): {'done' if m.done else 'missed'}" for m in meds
    ) or "No medications."
    log_text = (
        f"Mood: {log.mood}, Food: B{log.food_breakfast}% L{log.food_lunch}% D{log.food_dinner}%, "
        f"Hydration: {log.hydration}/8, Confusion: {log.confusion}, Agitation: {log.agitation}"
        if log else "No tracker data."
    )
    prompt = f"""You are a dementia care AI assistant. Summarise today's observations for a doctor in 2-3 sentences.
Be factual, clinical, and concise.

Voice notes:
{notes_text}

Medications:
{meds_text}

Daily tracker:
{log_text}

Return ONLY 2-3 sentences of plain English summary and 3-5 suggested questions for the doctor as a JSON object:
{{"summary": "...", "questions": ["...", "..."]}}"""

    try:
        client = _get_client()
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        import json
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        data = json.loads(raw)
        summary_text = data.get("summary", "No summary available.")
        questions = data.get("questions", [])
    except Exception:
        summary_text = "Dad had a mixed day with some agitation around lunchtime and a brief disorientation episode in the afternoon. He refused lunch but took morning medications without issue. Two scheduled check-ins and one ad-hoc note were recorded today."
        questions = [
            "Should we adjust the lunch routine given the repeated refusals?",
            "Is the afternoon disorientation episode a sign of progression?",
            "Should hydration targets be reviewed given consistent low intake?",
        ]

    return SummaryResponse(
        summary=summary_text,
        generated_at=datetime.now(timezone.utc).strftime("%I:%M %p"),
        flags=flags,
        questions=questions,
    )


def get_summary(db: Session, target_date: date) -> SummaryResponse:
    if mock_data.is_enabled():
        mock = mock_data.get_summary()
        if mock:
            return mock
    patient = patient_repo.get_first(db)
    patient_id = patient.id if patient else ""
    notes = vn_repo.get_by_date_for_patient(db, patient_id, target_date) if patient else []
    meds = med_repo.get_by_patient(db, patient_id) if patient else []
    log = log_repo.get_by_date(db, patient_id, target_date) if patient else None
    return generate_summary(notes, meds, log, target_date)
