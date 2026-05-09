from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from .repositories import patient as patient_repo, medication as med_repo, voice_note as vn_repo, daily_log as log_repo


def run_seed(db: Session) -> None:
    if patient_repo.get_first(db) is not None:
        return

    patient = patient_repo.create(db, name="Dad", caregiver_name="Sarah")
    db.flush()

    today = date.today()

    med_repo.create(
        db, patient.id,
        name="Donepezil 10mg",
        note="Alzheimer's · once daily",
        time_str="08:00",
        done=True,
        voice_note_text="Took it without fuss this morning.",
    )
    med_repo.create(
        db, patient.id,
        name="Amlodipine 5mg",
        note="Blood pressure",
        time_str="08:00",
        done=True,
    )
    med_repo.create(
        db, patient.id,
        name="Donepezil 10mg",
        note="Evening dose",
        time_str="21:00",
        done=False,
    )
    db.commit()

    vn_repo.create(
        db,
        patient_id=patient.id,
        transcript="Dad had a good morning, recognised me right away. Ate about half his breakfast. No episodes.",
        categories=["mood", "food", "recognition"],
        ai_tags=["recognition-good", "appetite-50pct", "mood-positive"],
        severity="low",
        note_type="scheduled",
        slot="9AM",
        created_at=datetime(today.year, today.month, today.day, 10, 23, tzinfo=timezone.utc),
    )
    vn_repo.create(
        db,
        patient_id=patient.id,
        transcript="Refused lunch. Kept asking for mum. Mild agitation, settled after 20 min of music.",
        categories=["food", "behaviour", "mood"],
        ai_tags=["appetite-0pct", "agitation-mild", "behaviour-repetitive"],
        severity="medium",
        note_type="scheduled",
        slot="12PM",
        created_at=datetime(today.year, today.month, today.day, 13, 14, tzinfo=timezone.utc),
    )
    vn_repo.create(
        db,
        patient_id=patient.id,
        transcript="Brief episode — didn't recognise the living room. Lasted about 5 minutes, then calm again.",
        categories=["recognition", "incident"],
        ai_tags=["recognition-poor", "episode-brief", "disorientation"],
        severity="high",
        note_type="adhoc",
        created_at=datetime(today.year, today.month, today.day, 14, 41, tzinfo=timezone.utc),
    )

    log_repo.upsert(
        db,
        patient_id=patient.id,
        target_date=today,
        mood=2,
        food_breakfast=75,
        food_lunch=0,
        food_dinner=50,
        hydration=3,
        confusion="Moderate",
        agitation="Mild",
        wandering="No",
        recognition="Partial",
        hallucinations="None",
        sleep_disruptions=2,
    )
