"""
Reset and seed Firestore with comprehensive demo data for the Pulse app.

Run from the repository root:
  python seed_data.py

Collections reset by this script:
  - patients
  - caregivers
  - medications
  - voice_notes
  - daily_wellbeing
  - reports
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.firebase_client import get_firestore_client


def utc(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


PATIENT_ID = "patient_demo_dad"
CAREGIVER_ID = "caregiver_demo_josanna"

MEDICATION_IDS = {
    "donepezil": "med_donepezil_10mg",
    "memantine": "med_memantine_5mg",
    "amlodipine": "med_amlodipine_5mg",
}

VOICE_NOTE_IDS = {
    "wellbeing_0509": "vn_daily_20260509_evening",
    "adhoc_0509": "vn_adhoc_20260509_living_room",
    "adhoc_0508": "vn_adhoc_20260508_after_lunch",
    "med_0508": "vn_medication_20260508_memantine",
    "adhoc_0507": "vn_adhoc_20260507_bus_stop",
    "wellbeing_0506": "vn_daily_20260506_morning",
    "med_0505": "vn_medication_20260505_donepezil",
}

REPORT_IDS = {
    "weekly": "report_20260501_20260509",
    "recent": "report_20260506_20260509",
}


PATIENTS = {
    PATIENT_ID: {
        "name": "Mr Tan",
        "caregiver_name": "Josanna",
        "created_at": utc(2026, 5, 1, 8, 0),
        "updated_at": utc(2026, 5, 9, 21, 0),
    },
}

CAREGIVERS = {
    CAREGIVER_ID: {
        "name": "Josanna",
        "dob": "1988-09-22",
        "patient_id": PATIENT_ID,
        "created_at": utc(2026, 5, 1, 8, 0),
        "updated_at": utc(2026, 5, 9, 21, 0),
    },
}

MEDICATIONS = {
    MEDICATION_IDS["donepezil"]: {
        "patient_id": PATIENT_ID,
        "name": "Donepezil 10mg",
        "note": "Alzheimer's support · once daily after breakfast",
        "time_str": "08:00",
        "done": True,
        "voice_note_text": "Took it calmly with water after breakfast.",
        "created_at": utc(2026, 5, 1, 8, 0),
        "updated_at": utc(2026, 5, 9, 8, 12),
    },
    MEDICATION_IDS["memantine"]: {
        "patient_id": PATIENT_ID,
        "name": "Memantine 5mg",
        "note": "Evening dose · watch for sleepiness",
        "time_str": "20:00",
        "done": False,
        "voice_note_text": "Refused it at first and needed a second attempt.",
        "created_at": utc(2026, 5, 1, 8, 5),
        "updated_at": utc(2026, 5, 8, 20, 20),
    },
    MEDICATION_IDS["amlodipine"]: {
        "patient_id": PATIENT_ID,
        "name": "Amlodipine 5mg",
        "note": "Blood pressure · once daily",
        "time_str": "09:00",
        "done": True,
        "voice_note_text": None,
        "created_at": utc(2026, 5, 1, 8, 10),
        "updated_at": utc(2026, 5, 9, 9, 5),
    },
}

VOICE_NOTES = {
    VOICE_NOTE_IDS["adhoc_0509"]: {
        "patient_id": PATIENT_ID,
        "transcript": "Mr Tan did not recognise the living room for about five minutes after waking from his nap, then settled down again.",
        "note_type": "adhoc",
        "language": "en",
        "med_id": None,
        "date": "2026-05-09",
        "created_at": utc(2026, 5, 9, 14, 41),
        "updated_at": utc(2026, 5, 9, 14, 41),
    },
    VOICE_NOTE_IDS["wellbeing_0509"]: {
        "patient_id": PATIENT_ID,
        "transcript": "He slept earlier than usual, woke up late, ate less at dinner, and looked a bit withdrawn tonight.",
        "note_type": "daily_wellbeing",
        "language": "en",
        "med_id": None,
        "date": "2026-05-09",
        "created_at": utc(2026, 5, 9, 20, 0),
        "updated_at": utc(2026, 5, 9, 20, 0),
    },
    VOICE_NOTE_IDS["adhoc_0508"]: {
        "patient_id": PATIENT_ID,
        "transcript": "After lunch he kept asking where his wife was and needed repeated reassurance for about twenty minutes.",
        "note_type": "adhoc",
        "language": "en",
        "med_id": None,
        "date": "2026-05-08",
        "created_at": utc(2026, 5, 8, 13, 25),
        "updated_at": utc(2026, 5, 8, 13, 25),
    },
    VOICE_NOTE_IDS["med_0508"]: {
        "patient_id": PATIENT_ID,
        "transcript": "He hesitated on the evening memantine and finally took it after I mixed it with yoghurt.",
        "note_type": "medication",
        "language": "en",
        "med_id": MEDICATION_IDS["memantine"],
        "date": "2026-05-08",
        "created_at": utc(2026, 5, 8, 20, 18),
        "updated_at": utc(2026, 5, 8, 20, 18),
    },
    VOICE_NOTE_IDS["adhoc_0507"]: {
        "patient_id": PATIENT_ID,
        "transcript": "At the bus stop he became anxious because he thought he was late for work and tried to walk away.",
        "note_type": "adhoc",
        "language": "en",
        "med_id": None,
        "date": "2026-05-07",
        "created_at": utc(2026, 5, 7, 18, 2),
        "updated_at": utc(2026, 5, 7, 18, 2),
    },
    VOICE_NOTE_IDS["wellbeing_0506"]: {
        "patient_id": PATIENT_ID,
        "transcript": "He was in a better mood this morning and appetite was back to normal after breakfast.",
        "note_type": "daily_wellbeing",
        "language": "en",
        "med_id": None,
        "date": "2026-05-06",
        "created_at": utc(2026, 5, 6, 9, 10),
        "updated_at": utc(2026, 5, 6, 9, 10),
    },
    VOICE_NOTE_IDS["med_0505"]: {
        "patient_id": PATIENT_ID,
        "transcript": "Donepezil was taken on time without difficulty this morning.",
        "note_type": "medication",
        "language": "en",
        "med_id": MEDICATION_IDS["donepezil"],
        "date": "2026-05-05",
        "created_at": utc(2026, 5, 5, 8, 7),
        "updated_at": utc(2026, 5, 5, 8, 7),
    },
}

DAILY_WELLBEING = {
    "dw_20260509": {
        "patient_id": PATIENT_ID,
        "date": "2026-05-09",
        "sleep_pattern": "earlier_sleep_later_wake",
        "appetite": "eating_less",
        "mood": "sad",
        "voice_note_id": VOICE_NOTE_IDS["wellbeing_0509"],
        "created_at": utc(2026, 5, 9, 20, 5),
        "updated_at": utc(2026, 5, 9, 20, 5),
    },
    "dw_20260508": {
        "patient_id": PATIENT_ID,
        "date": "2026-05-08",
        "sleep_pattern": "same",
        "appetite": "same",
        "mood": "neutral",
        "voice_note_id": None,
        "created_at": utc(2026, 5, 8, 21, 0),
        "updated_at": utc(2026, 5, 8, 21, 0),
    },
    "dw_20260507": {
        "patient_id": PATIENT_ID,
        "date": "2026-05-07",
        "sleep_pattern": "later_sleep_earlier_wake",
        "appetite": "eating_less",
        "mood": "upset",
        "voice_note_id": None,
        "created_at": utc(2026, 5, 7, 21, 10),
        "updated_at": utc(2026, 5, 7, 21, 10),
    },
    "dw_20260506": {
        "patient_id": PATIENT_ID,
        "date": "2026-05-06",
        "sleep_pattern": "same",
        "appetite": "eating_more",
        "mood": "happy",
        "voice_note_id": VOICE_NOTE_IDS["wellbeing_0506"],
        "created_at": utc(2026, 5, 6, 9, 15),
        "updated_at": utc(2026, 5, 6, 9, 15),
    },
}

REPORTS = {
    REPORT_IDS["weekly"]: {
        "patient_id": PATIENT_ID,
        "title": "Report #1",
        "start_date": "2026-05-01",
        "end_date": "2026-05-09",
        "summary": "Mr Tan had a mixed week with fluctuating confusion, a noticeable dip in appetite on 9 May 2026, and repeated evening anxiety. Medication adherence was mostly good, though the evening memantine dose required extra prompting.",
        "flags": [
            {"severity": "red", "text": "On 9 May 2026 he did not recognise the living room for several minutes after a nap."},
            {"severity": "amber", "text": "Evening anxiety and perseveration increased on 7 and 8 May 2026."},
            {"severity": "amber", "text": "Reduced appetite was observed on 9 May 2026."},
        ],
        "generated_at": utc(2026, 5, 9, 21, 0),
        "created_at": utc(2026, 5, 9, 21, 0),
        "updated_at": utc(2026, 5, 9, 21, 0),
    },
    REPORT_IDS["recent"]: {
        "patient_id": PATIENT_ID,
        "title": "Report #2",
        "start_date": "2026-05-06",
        "end_date": "2026-05-09",
        "summary": "Across 6 to 9 May 2026, Mr Tan showed more evening distress than morning distress. Sleep changes were mild but appetite and mood worsened by 9 May 2026.",
        "flags": [
            {"severity": "amber", "text": "Evening behaviour became more unsettled approaching 9 May 2026."},
            {"severity": "amber", "text": "Appetite dropped below usual baseline on 9 May 2026."},
        ],
        "generated_at": utc(2026, 5, 9, 21, 15),
        "created_at": utc(2026, 5, 9, 21, 15),
        "updated_at": utc(2026, 5, 9, 21, 15),
    },
}


COLLECTIONS = [
    ("reports", REPORTS),
    ("daily_wellbeing", DAILY_WELLBEING),
    ("voice_notes", VOICE_NOTES),
    ("medications", MEDICATIONS),
    ("caregivers", CAREGIVERS),
    ("patients", PATIENTS),
]


def clear_collection(client, name: str) -> int:
    docs = list(client.collection(name).stream())
    for doc in docs:
        doc.reference.delete()
    return len(docs)


def seed_collection(client, name: str, documents: dict[str, dict]) -> int:
    for doc_id, payload in documents.items():
        client.collection(name).document(doc_id).set(payload)
    return len(documents)


def run() -> None:
    client = get_firestore_client()

    print("Resetting Firestore collections...")
    for collection_name, _ in COLLECTIONS:
        deleted = clear_collection(client, collection_name)
        print(f"  - Cleared {deleted} document(s) from '{collection_name}'")

    print("Seeding Firestore collections...")
    for collection_name, documents in reversed(COLLECTIONS):
        created = seed_collection(client, collection_name, documents)
        print(f"  - Seeded {created} document(s) into '{collection_name}'")

    print("")
    print("Seed complete.")
    print(f"Primary patient ID: {PATIENT_ID}")
    print(f"Primary caregiver name: {PATIENTS[PATIENT_ID]['caregiver_name']}")


if __name__ == "__main__":
    run()
