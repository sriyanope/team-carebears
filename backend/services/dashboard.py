from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from ..repositories import patient as patient_repo, voice_note as vn_repo, medication as med_repo, daily_log as log_repo
from ..schemas.dashboard import ScheduleSlot, PatientInfo, DashboardMetrics, DashboardResponse

SLOTS = [
    ("9AM", "9 AM"),
    ("12PM", "12 PM"),
    ("3PM", "3 PM"),
    ("6PM", "6 PM"),
    ("9PM", "9 PM"),
]

SLOT_HOURS = {"9AM": 9, "12PM": 12, "3PM": 15, "6PM": 18, "9PM": 21}


def get_dashboard(db: Session) -> DashboardResponse:
    patient = patient_repo.get_first(db)
    today = date.today()
    patient_id = patient.id if patient else ""
    notes = vn_repo.get_by_date_for_patient(db, patient_id, today) if patient else []
    meds = med_repo.get_by_patient(db, patient_id) if patient else []
    log = log_repo.get_by_date(db, patient_id, today)

    meds_done = sum(1 for m in meds if m.done)
    food_avg = 0
    hydration = 0
    if log:
        food_avg = (log.food_breakfast + log.food_lunch + log.food_dinner) // 3
        hydration = log.hydration

    current_hour = datetime.now(timezone.utc).hour
    done_slots = {n.slot for n in notes if n.slot}

    schedule = []
    for slot_key, slot_label in SLOTS:
        if slot_key in done_slots:
            status = "done"
        elif SLOT_HOURS[slot_key] <= current_hour < SLOT_HOURS[slot_key] + 3:
            status = "current"
        else:
            status = "upcoming"
        schedule.append(ScheduleSlot(slot=slot_key, label=slot_label, status=status))

    days_tracking = max(1, (today - date(today.year, 1, 1)).days + 1)

    return DashboardResponse(
        patient=PatientInfo(
            name=patient.name if patient else "Dad",
            caregiver_name=patient.caregiver_name if patient else "Sarah",
            tracking_days=days_tracking,
        ),
        metrics=DashboardMetrics(
            meds_done=meds_done,
            meds_total=len(meds),
            food_avg=food_avg,
            hydration=hydration,
            notes_count=len(notes),
        ),
        schedule=schedule,
        recent_notes=list(reversed(notes[-5:])),
    )
