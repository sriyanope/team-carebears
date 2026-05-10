from . import mock_data
from ..repositories import caregiver as caregiver_repo
from ..repositories import patient as patient_repo
from ..schemas.onboarding import (
    OnboardingCaregiverResponse,
    OnboardingPatientResponse,
    OnboardingResponse,
)


def get(patient_id: str | None = None) -> OnboardingResponse | None:
    if mock_data.is_enabled():
        return mock_data.get_onboarding()

    patient = patient_repo.get_by_id(None, patient_id) if patient_id else patient_repo.get_first(None)
    if not patient:
        return None

    caregiver = caregiver_repo.get_by_patient_id(patient.id) if patient.id else None
    return OnboardingResponse(
        patient=OnboardingPatientResponse(id=patient.id, name=patient.name),
        caregiver=OnboardingCaregiverResponse(
            id=caregiver.id if caregiver else None,
            name=caregiver.name if caregiver else patient.caregiver_name,
        ),
    )


def upsert(
    *,
    patient_name: str,
    caregiver_name: str,
    patient_id: str | None = None,
    caregiver_id: str | None = None,
) -> OnboardingResponse:
    if mock_data.is_enabled():
        return OnboardingResponse(
            patient=OnboardingPatientResponse(id=patient_id or "mock-patient", name=patient_name),
            caregiver=OnboardingCaregiverResponse(id=caregiver_id or "mock-caregiver", name=caregiver_name),
        )

    patient = None
    if patient_id:
        patient = patient_repo.get_by_id(None, patient_id)
        if patient:
            patient = patient_repo.update(None, patient, name=patient_name, caregiver_name=caregiver_name)

    if patient is None:
        patient = patient_repo.create(None, patient_name, caregiver_name)

    caregiver = None
    if caregiver_id:
        caregiver = caregiver_repo.get_by_id(caregiver_id)
        if caregiver:
            caregiver = caregiver_repo.update(caregiver, name=caregiver_name)

    if caregiver is None:
        caregiver = caregiver_repo.create(name=caregiver_name, patient_id=patient.id)

    return OnboardingResponse(
        patient=OnboardingPatientResponse(id=patient.id, name=patient.name),
        caregiver=OnboardingCaregiverResponse(id=caregiver.id, name=caregiver.name),
    )


def patch(
    *,
    patient_name: str | None = None,
    caregiver_name: str | None = None,
    patient_id: str | None = None,
    caregiver_id: str | None = None,
) -> OnboardingResponse | None:
    if mock_data.is_enabled():
        current = mock_data.get_onboarding()
        return current

    patient = patient_repo.get_by_id(None, patient_id) if patient_id else patient_repo.get_first(None)
    if patient is None:
        return None

    caregiver = caregiver_repo.get_by_id(caregiver_id) if caregiver_id else None

    updated = patient_repo.update(
        None,
        patient,
        name=patient_name,
        caregiver_name=caregiver_name,
    )
    if caregiver and caregiver_name:
        caregiver = caregiver_repo.update(caregiver, name=caregiver_name)
    return OnboardingResponse(
        patient=OnboardingPatientResponse(id=updated.id, name=updated.name),
        caregiver=OnboardingCaregiverResponse(
            id=caregiver.id if caregiver else None,
            name=caregiver.name if caregiver else updated.caregiver_name,
        ),
    )
