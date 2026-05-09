"""
Run directly to populate Firestore with clean test data:
  cd backend && python seed_data.py
"""
import sys
from datetime import datetime, timezone

from backend.firebase_client import get_firestore_client


def run():
    client = get_firestore_client()

    # Get first patient
    docs = list(client.collection("patients").limit(1).stream())
    if not docs:
        print("ERROR: No patient found in 'patients' collection. Cannot seed data.")
        sys.exit(1)
    patient_id = docs[0].id
    print(f"Seeding data for patient: {patient_id}")

    # Delete all existing voice_notes
    existing = list(client.collection("voice_notes").stream())
    for doc in existing:
        doc.reference.delete()
    print(f"Deleted {len(existing)} existing voice note(s)")

    # Seed voice_notes
    voice_notes = [
        {
            "patient_id": patient_id,
            "transcript": "Dad had an episode — didn't recognise the living room. Lasted about 5 minutes, then calm again.",
            "note_type": "adhoc",
            "language": "en",
            "med_id": None,
            "date": "2026-05-09",
            "created_at": datetime(2026, 5, 9, 14, 41, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 9, 14, 41, 0, tzinfo=timezone.utc),
        },
        {
            "patient_id": patient_id,
            "transcript": "He seemed more confused than usual after lunch. Kept asking where mum was.",
            "note_type": "adhoc",
            "language": "en",
            "med_id": None,
            "date": "2026-05-08",
            "created_at": datetime(2026, 5, 8, 11, 30, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 8, 11, 30, 0, tzinfo=timezone.utc),
        },
        {
            "patient_id": patient_id,
            "transcript": "Good morning today, ate most of his breakfast. Took medication on time.",
            "note_type": "daily_wellbeing",
            "language": "en",
            "med_id": None,
            "date": "2026-05-07",
            "created_at": datetime(2026, 5, 7, 9, 15, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 7, 9, 15, 0, tzinfo=timezone.utc),
        },
    ]

    for note in voice_notes:
        doc_ref = client.collection("voice_notes").document()
        doc_ref.set(note)
    print(f"Created {len(voice_notes)} voice note(s)")

    # Seed daily_wellbeing
    wellbeing_entries = [
        {
            "patient_id": patient_id,
            "date": "2026-05-09",
            "sleep_pattern": "earlier_sleep_later_wake",
            "appetite": "eating_less",
            "mood": "sad",
            "voice_note_id": None,
            "created_at": datetime(2026, 5, 9, 20, 0, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 5, 9, 20, 0, 0, tzinfo=timezone.utc),
        },
    ]

    for entry in wellbeing_entries:
        doc_ref = client.collection("daily_wellbeing").document()
        doc_ref.set(entry)
    print(f"Created {len(wellbeing_entries)} daily wellbeing entry(s)")

    print("Seeding complete.")


if __name__ == "__main__":
    run()
