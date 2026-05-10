'use client'

import { FormEvent, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { postOnboarding } from '@/lib/api'
import { useLanguage } from '@/lib/LanguageContext'
import {
  OnboardingProfile,
  readOnboardingProfile,
  saveOnboardingProfile,
} from '@/lib/onboarding'

type GateStep = 'checking' | 'onboarding' | 'welcome' | 'ready'

export default function OnboardingGate({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { t } = useLanguage()
  const [step, setStep] = useState<GateStep>('checking')
  const [profile, setProfile] = useState<OnboardingProfile | null>(null)
  const [caregiverName, setCaregiverName] = useState('')
  const [patientName, setPatientName] = useState('')
  const [patientAge, setPatientAge] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    const savedProfile = readOnboardingProfile()
    if (savedProfile) {
      setProfile(savedProfile)
      setStep('ready')
      return
    }

    setStep('onboarding')
  }, [])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const age = Number(patientAge)
    const nextProfile = {
      caregiverName: caregiverName.trim(),
      patientName: patientName.trim(),
      patientAge: age,
    }

    if (!nextProfile.caregiverName || !nextProfile.patientName || age < 1) return

    setIsSaving(true)
    setErrorMessage(null)

    const onboarding = await postOnboarding({
      patient: { id: profile?.patientId, name: nextProfile.patientName },
      caregiver: { id: profile?.caregiverId, name: nextProfile.caregiverName },
    })

    if (!onboarding) {
      setIsSaving(false)
      setErrorMessage(t('onboardingSaveError'))
      return
    }

    const storedProfile = {
      ...nextProfile,
      patientId: onboarding.patient_id,
      caregiverId: onboarding.caregiver_id,
    }
    saveOnboardingProfile(storedProfile)
    setProfile(storedProfile)
    setIsSaving(false)
    setStep('welcome')
  }

  function enterApp() {
    setStep('ready')
    router.replace('/')
  }

  if (step === 'checking') {
    return <div className="min-h-screen bg-stone-50" />
  }

  if (step === 'welcome' && profile) {
    return (
      <main className="min-h-screen bg-stone-50 px-5 py-6">
        <section className="flex min-h-[calc(100vh-48px)] flex-col justify-between rounded-2xl border border-blue-100 bg-white p-5">
          <div className="space-y-6">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-4xl">
              👋
            </div>
            <div className="space-y-3">
              <p className="text-xs font-medium uppercase tracking-widest text-stone-400">{t('allSet')}</p>
              <h1 className="font-serif text-[42px] leading-none text-stone-900">
                {t('hiName', { name: profile.caregiverName })}
              </h1>
              <p className="text-lg leading-relaxed text-stone-700">
                {t('welcomeMessage', { name: profile.patientName })}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="rounded-2xl border border-stone-100 bg-blue-50 p-4">
              <p className="text-xs font-medium uppercase tracking-widest text-blue-700">{t('careProfile')}</p>
              <div className="mt-3 flex items-center gap-3">
                <span className="text-4xl">🧓</span>
                <div>
                  <p className="text-xl font-semibold text-stone-900">{profile.patientName}</p>
                  <p className="text-stone-400">{t('yearsOld', { age: profile.patientAge })}</p>
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={enterApp}
              className="min-h-14 w-full rounded-2xl bg-blue-500 px-5 py-4 text-lg font-semibold text-white active:scale-[0.99]"
            >
              {t('startCare')}
            </button>
          </div>
        </section>
      </main>
    )
  }

  if (step === 'onboarding') {
    const canContinue = caregiverName.trim() && patientName.trim() && Number(patientAge) > 0

    return (
      <main className="min-h-screen bg-stone-50 px-5 py-6">
        <form onSubmit={handleSubmit} className="flex min-h-[calc(100vh-48px)] flex-col justify-between">
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-4xl">
                🫶
              </div>
              <div className="space-y-2">
                <p className="text-xs font-medium uppercase tracking-widest text-stone-400">{t('welcomeToSilverPulse')}</p>
                <h1 className="font-serif text-[42px] leading-none text-stone-900">{t('setupCare')}</h1>
                <p className="text-lg leading-relaxed text-stone-700">
                  {t('onboardingIntro')}
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <label className="block rounded-2xl border border-stone-100 bg-white p-4">
                <span className="mb-3 flex items-center gap-3 text-lg font-semibold text-stone-900">
                  <span className="text-3xl">🙂</span>
                  {t('yourName')}
                </span>
                <input
                  value={caregiverName}
                  onChange={(event) => setCaregiverName(event.target.value)}
                  className="min-h-14 w-full rounded-2xl border border-stone-100 bg-stone-50 px-4 text-lg text-stone-900 outline-none focus:border-blue-500"
                  placeholder="e.g. Mei Lin"
                  autoComplete="given-name"
                />
              </label>

              <label className="block rounded-2xl border border-stone-100 bg-white p-4">
                <span className="mb-3 flex items-center gap-3 text-lg font-semibold text-stone-900">
                  <span className="text-3xl">🧓</span>
                  {t('patientName')}
                </span>
                <input
                  value={patientName}
                  onChange={(event) => setPatientName(event.target.value)}
                  className="min-h-14 w-full rounded-2xl border border-stone-100 bg-stone-50 px-4 text-lg text-stone-900 outline-none focus:border-blue-500"
                  placeholder="e.g. Mum"
                  autoComplete="off"
                />
              </label>

              <label className="block rounded-2xl border border-stone-100 bg-white p-4">
                <span className="mb-3 flex items-center gap-3 text-lg font-semibold text-stone-900">
                  <span className="text-3xl">🎂</span>
                  {t('patientAge')}
                </span>
                <input
                  value={patientAge}
                  onChange={(event) => setPatientAge(event.target.value)}
                  className="min-h-14 w-full rounded-2xl border border-stone-100 bg-stone-50 px-4 text-lg text-stone-900 outline-none focus:border-blue-500"
                  placeholder="e.g. 78"
                  inputMode="numeric"
                  type="number"
                  min="1"
                  max="120"
                />
              </label>
            </div>

            {errorMessage && (
              <div className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-500">
                {errorMessage}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={!canContinue || isSaving}
            className="mt-6 min-h-14 w-full rounded-2xl bg-blue-500 px-5 py-4 text-lg font-semibold text-white active:scale-[0.99] disabled:bg-stone-100 disabled:text-stone-400"
          >
            {isSaving ? t('saving') : t('continue')}
          </button>
        </form>
      </main>
    )
  }

  return children
}
