export interface OnboardingProfile {
  caregiverName: string
  patientName: string
  patientAge: number
}

export const ONBOARDING_STORAGE_KEY = 'silverpulse:onboarding-profile'

export function readOnboardingProfile(): OnboardingProfile | null {
  if (typeof window === 'undefined') return null

  try {
    const stored = window.sessionStorage.getItem(ONBOARDING_STORAGE_KEY)
    if (!stored) return null

    const parsed = JSON.parse(stored) as Partial<OnboardingProfile>
    if (!parsed.caregiverName || !parsed.patientName || !parsed.patientAge) return null

    return {
      caregiverName: parsed.caregiverName,
      patientName: parsed.patientName,
      patientAge: parsed.patientAge,
    }
  } catch {
    return null
  }
}

export function saveOnboardingProfile(profile: OnboardingProfile): void {
  window.sessionStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(profile))
}
