from pydantic import BaseModel


class OnboardingPatientRequest(BaseModel):
    id: str | None = None
    name: str


class OnboardingCaregiverRequest(BaseModel):
    id: str | None = None
    name: str


class OnboardingRequest(BaseModel):
    patient: OnboardingPatientRequest
    caregiver: OnboardingCaregiverRequest


class OnboardingPatientUpdate(BaseModel):
    id: str | None = None
    name: str | None = None


class OnboardingCaregiverUpdate(BaseModel):
    id: str | None = None
    name: str | None = None


class OnboardingUpdateRequest(BaseModel):
    patient: OnboardingPatientUpdate | None = None
    caregiver: OnboardingCaregiverUpdate | None = None


class OnboardingPatientResponse(BaseModel):
    id: str | None = None
    name: str


class OnboardingCaregiverResponse(BaseModel):
    id: str | None = None
    name: str


class OnboardingResponse(BaseModel):
    patient: OnboardingPatientResponse
    caregiver: OnboardingCaregiverResponse
