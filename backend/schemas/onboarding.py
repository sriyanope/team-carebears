from pydantic import BaseModel


class OnboardingPatientRequest(BaseModel):
    name: str


class OnboardingCaregiverRequest(BaseModel):
    name: str


class OnboardingRequest(BaseModel):
    patient: OnboardingPatientRequest
    caregiver: OnboardingCaregiverRequest


class OnboardingPatientUpdate(BaseModel):
    name: str | None = None


class OnboardingCaregiverUpdate(BaseModel):
    name: str | None = None


class OnboardingUpdateRequest(BaseModel):
    patient: OnboardingPatientUpdate | None = None
    caregiver: OnboardingCaregiverUpdate | None = None


class OnboardingPatientResponse(BaseModel):
    name: str


class OnboardingCaregiverResponse(BaseModel):
    name: str


class OnboardingResponse(BaseModel):
    patient: OnboardingPatientResponse
    caregiver: OnboardingCaregiverResponse
