from fastapi import APIRouter, HTTPException

from ..schemas.onboarding import OnboardingRequest, OnboardingResponse, OnboardingUpdateRequest
from ..services import onboarding as onboarding_service

router = APIRouter()


@router.get("/api/onboarding", response_model=OnboardingResponse)
def get_onboarding():
    onboarding = onboarding_service.get()
    if onboarding is None:
        raise HTTPException(status_code=404, detail="No onboarding data found")
    return onboarding


@router.post("/api/onboarding", response_model=OnboardingResponse)
def create_onboarding(body: OnboardingRequest):
    return onboarding_service.upsert(
        patient_name=body.patient.name,
        caregiver_name=body.caregiver.name,
    )


@router.patch("/api/onboarding", response_model=OnboardingResponse)
def update_onboarding(body: OnboardingUpdateRequest):
    onboarding = onboarding_service.patch(
        patient_name=body.patient.name if body.patient else None,
        caregiver_name=body.caregiver.name if body.caregiver else None,
    )
    if onboarding is None:
        raise HTTPException(status_code=404, detail="No onboarding data found")
    return onboarding
