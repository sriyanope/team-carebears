from . import mock_data
from ..repositories import patient as patient_repo
from ..schemas.onboarding import (
    OnboardingCaregiverResponse,
    OnboardingPatientResponse,
    OnboardingResponse,
)


def get() -> OnboardingResponse | None:
    if mock_data.is_enabled():
        return mock_data.get_onboarding()

    patient = patient_repo.get_first(None)
    if not patient:
        return None

    return OnboardingResponse(
        patient=OnboardingPatientResponse(name=patient.name),
        caregiver=OnboardingCaregiverResponse(name=patient.caregiver_name),
    )


def upsert(*, patient_name: str, caregiver_name: str) -> OnboardingResponse:
    if mock_data.is_enabled():
        return OnboardingResponse(
            patient=OnboardingPatientResponse(name=patient_name),
            caregiver=OnboardingCaregiverResponse(name=caregiver_name),
        )

    patient = patient_repo.upsert_profile(None, name=patient_name, caregiver_name=caregiver_name)
    return OnboardingResponse(
        patient=OnboardingPatientResponse(name=patient.name),
        caregiver=OnboardingCaregiverResponse(name=patient.caregiver_name),
    )


def patch(*, patient_name: str | None = None, caregiver_name: str | None = None) -> OnboardingResponse | None:
    if mock_data.is_enabled():
        current = mock_data.get_onboarding()
        return current

    patient = patient_repo.get_first(None)
    if patient is None:
        return None

    updated = patient_repo.update(
        None,
        patient,
        name=patient_name,
        caregiver_name=caregiver_name,
    )
    return OnboardingResponse(
        patient=OnboardingPatientResponse(name=updated.name),
        caregiver=OnboardingCaregiverResponse(name=updated.caregiver_name),
    )
