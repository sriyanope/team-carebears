import { readOnboardingProfile, saveOnboardingProfile } from '@/lib/onboarding'

export type AppLanguage = 'en' | 'zh' | 'ms' | 'ta'

export interface PatientInfo {
  patient_name: string
  caregiver_name: string
}

export interface OnboardingPayload {
  patient: {
    id?: string
    name: string
  }
  caregiver: {
    id?: string
    name: string
  }
}

export interface VoiceNote {
  id: string
  patient_id: string
  transcript: string
  note_type: string
  language: string
  med_id: string | null
  created_at: string
  updated_at: string
}

export interface Medication {
  id: string
  patient_id: string
  name: string
  note: string | null
  dosage: string | null
  frequency_per_week: number | null
  special_instructions: string | null
  expiry_date: string | null
  time_str: string
  done: boolean
  voice_note_text: string | null
  created_at: string
  updated_at: string
}

export interface MedicationCreatePayload {
  name: string
  dosage: string
  frequency_per_week: number
  special_instructions?: string | null
  expiry_date?: string | null
}

export type MedicationUpdatePayload = Partial<MedicationCreatePayload>

export type SleepPattern = 'earlier_sleep_later_wake' | 'same' | 'later_sleep_earlier_wake'
export type Appetite = 'eating_less' | 'same' | 'eating_more'
export type Mood = 'happy' | 'ok' | 'neutral' | 'sad' | 'upset'

export interface DailyWellbeingEntry {
  id: string
  patient_id: string
  date: string
  sleep_pattern: SleepPattern
  appetite: Appetite
  mood: Mood
  voice_note_id: string | null
  voice_note_transcript?: string | null
  created_at: string
}

export interface DailyWellbeingRequest {
  patient_id?: string
  sleep_pattern: SleepPattern
  appetite: Appetite
  mood: Mood
  voice_note_id?: string
}

export interface ReportFlag {
  severity?: string
  text: string
}

export interface ReportSummary {
  id: string
  title: string
  start_date: string
  end_date: string
  generated_at: string
}

export interface ReportDetail extends ReportSummary {
  summary: string
  flags: ReportFlag[]
}

interface ReportContext {
  patient_id: string
}

interface MockOnboardingResponse {
  patient?: {
    id?: string
    name?: string
  }
  caregiver?: {
    id?: string
    name?: string
  }
}

interface OnboardingResult {
  patient_name: string
  caregiver_name: string
  patient_id?: string
  caregiver_id?: string
}

interface MockData {
  onboarding?: MockOnboardingResponse
  voice_notes?: VoiceNote[]
  medications?: Medication[]
  daily_wellbeing?: DailyWellbeingEntry[]
  reports?: ReportDetail[]
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') ?? ''
const MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === 'true' || process.env.NEXT_PUBLIC_MOCK_MODE === '1'
const MOCK_DATA_JSON = process.env.NEXT_PUBLIC_MOCK_DATA_JSON?.trim() ?? ''

let mockCache: MockData | null = null

function getMockData(): MockData {
  if (mockCache) return mockCache
  if (!MOCK_DATA_JSON) return {}
  try {
    mockCache = JSON.parse(MOCK_DATA_JSON) as MockData
  } catch {
    mockCache = {}
  }
  return mockCache
}

function withBase(path: string): string {
  return API_BASE ? `${API_BASE}${path}` : path
}

function getReportContext(): ReportContext | null {
  const profile = readOnboardingProfile()
  if (!profile) return null

  const patientId = profile.patientId?.trim()
  if (!patientId) return null

  return {
    patient_id: patientId,
  }
}

function getPatientId(): string | null {
  const profile = readOnboardingProfile()
  const patientId = profile?.patientId?.trim()
  return patientId || null
}

function withQuery(path: string, params: Record<string, string | null | undefined>): string {
  const query = new URLSearchParams()

  for (const [key, value] of Object.entries(params)) {
    if (value) query.set(key, value)
  }

  const queryString = query.toString()
  return queryString ? `${path}?${queryString}` : path
}

export async function getPatientInfo(): Promise<PatientInfo> {
  const sessionProfile = readOnboardingProfile()
  const patientId = sessionProfile?.patientId

  if (MOCK_MODE) {
    const onboarding = getMockData().onboarding
    return {
      patient_name: onboarding?.patient?.name || sessionProfile?.patientName || 'Dad',
      caregiver_name: onboarding?.caregiver?.name || sessionProfile?.caregiverName || 'Sarah',
    }
  }

  try {
    const url = patientId ? withQuery('/api/onboarding', { patient_id: patientId }) : '/api/onboarding'
    const res = await fetch(withBase(url))
    if (res.ok) {
      const data = (await res.json()) as MockOnboardingResponse
      if (sessionProfile && !sessionProfile.patientId && data.patient?.id) {
        saveOnboardingProfile({
          ...sessionProfile,
          patientId: data.patient.id,
          caregiverId: data.caregiver?.id ?? sessionProfile.caregiverId,
        })
      }
      return {
        patient_name: data.patient?.name || sessionProfile?.patientName || 'Dad',
        caregiver_name: data.caregiver?.name || sessionProfile?.caregiverName || 'Sarah',
      }
    }
  } catch {}

  return {
    patient_name: sessionProfile?.patientName || 'Dad',
    caregiver_name: sessionProfile?.caregiverName || 'Sarah',
  }
}

export async function postOnboarding(payload: OnboardingPayload): Promise<OnboardingResult | null> {
  if (MOCK_MODE) {
    return {
      patient_name: payload.patient.name,
      caregiver_name: payload.caregiver.name,
      patient_id: payload.patient.id ?? 'mock-patient',
      caregiver_id: payload.caregiver.id ?? 'mock-caregiver',
    }
  }

  try {
    const res = await fetch(withBase('/api/onboarding'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) return null

    const data = (await res.json()) as MockOnboardingResponse
    return {
      patient_name: data.patient?.name || payload.patient.name,
      caregiver_name: data.caregiver?.name || payload.caregiver.name,
      patient_id: data.patient?.id,
      caregiver_id: data.caregiver?.id,
    }
  } catch {
    return null
  }
}

export async function fetchVoiceNotes(date?: string): Promise<VoiceNote[] | null> {
  if (MOCK_MODE) return getMockData().voice_notes ?? null

  try {
    const patientId = getPatientId()
    if (!patientId) return null
    const url = date
      ? withQuery('/api/voice-notes', { target_date: date, patient_id: patientId })
      : withQuery('/api/voice-notes', { patient_id: patientId })
    const res = await fetch(withBase(url))
    if (!res.ok) return null
    return (await res.json()) as VoiceNote[]
  } catch {
    return null
  }
}

export async function postVoiceNote(
  audioBlob: Blob,
  noteType: string,
  language?: AppLanguage,
  medId?: string,
): Promise<VoiceNote | null> {
  const selectedLanguage = language ?? 'en'

  if (MOCK_MODE) {
    const now = new Date().toISOString()
    return {
      id: crypto.randomUUID(),
      patient_id: 'mock-patient',
      transcript: 'Mock transcript saved.',
      note_type: noteType,
      language: selectedLanguage,
      med_id: medId ?? null,
      created_at: now,
      updated_at: now,
    }
  }

  try {
    const patientId = getPatientId()
    if (!patientId) return null
    const form = new FormData()
    form.append('audio', audioBlob, 'recording.webm')
    form.append('type', noteType)
    form.append('language', selectedLanguage)
    form.append('patient_id', patientId)
    if (medId) form.append('med_id', medId)

    const res = await fetch(withBase('/api/voice-notes'), {
      method: 'POST',
      body: form,
    })
    if (!res.ok) return null
    return (await res.json()) as VoiceNote
  } catch {
    return null
  }
}

export async function fetchMedications(): Promise<Medication[] | null> {
  if (MOCK_MODE) return getMockData().medications ?? null

  try {
    const patientId = getPatientId()
    if (!patientId) return null
    const res = await fetch(withBase(withQuery('/api/medications', { patient_id: patientId })))
    if (!res.ok) return null
    return (await res.json()) as Medication[]
  } catch {
    return null
  }
}

export async function fetchMedication(id: string): Promise<Medication | null> {
  if (MOCK_MODE) {
    const meds = getMockData().medications ?? []
    return meds.find((med) => med.id === id) ?? null
  }

  try {
    const res = await fetch(withBase(`/api/medications/${id}`))
    if (!res.ok) return null
    return (await res.json()) as Medication
  } catch {
    return null
  }
}

export async function postMedication(payload: MedicationCreatePayload): Promise<Medication | null> {
  if (MOCK_MODE) {
    const now = new Date().toISOString()
    return {
      id: crypto.randomUUID(),
      patient_id: 'mock-patient',
      name: payload.name,
      note: [
        `Dosage: ${payload.dosage}`,
        `${payload.frequency_per_week} times/week`,
        payload.special_instructions ? `Instructions: ${payload.special_instructions}` : '',
        payload.expiry_date ? `Expires: ${payload.expiry_date}` : '',
      ].filter(Boolean).join(' | '),
      dosage: payload.dosage,
      frequency_per_week: payload.frequency_per_week,
      special_instructions: payload.special_instructions ?? null,
      expiry_date: payload.expiry_date ?? null,
      time_str: '09:00',
      done: false,
      voice_note_text: null,
      created_at: now,
      updated_at: now,
    }
  }

  try {
    const res = await fetch(withBase('/api/medications'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) return null
    return (await res.json()) as Medication
  } catch {
    return null
  }
}

export async function updateMedicationDetails(
  id: string,
  payload: MedicationUpdatePayload,
): Promise<Medication | null> {
  if (MOCK_MODE) {
    const meds = getMockData().medications ?? []
    const found = meds.find((med) => med.id === id) ?? meds[0]
    if (!found) return null

    const dosage = payload.dosage ?? found.dosage ?? ''
    const frequency = payload.frequency_per_week ?? found.frequency_per_week ?? 0
    const instructions = payload.special_instructions ?? found.special_instructions ?? ''
    const expiry = payload.expiry_date ?? found.expiry_date ?? ''

    return {
      ...found,
      ...payload,
      note: [
        dosage ? `Dosage: ${dosage}` : '',
        frequency ? `${frequency} times/week` : '',
        instructions ? `Instructions: ${instructions}` : '',
        expiry ? `Expires: ${expiry}` : '',
      ].filter(Boolean).join(' | '),
      updated_at: new Date().toISOString(),
    }
  }

  try {
    const res = await fetch(withBase(`/api/medications/${id}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) return null
    return (await res.json()) as Medication
  } catch {
    return null
  }
}

export async function deleteMedication(id: string): Promise<boolean> {
  if (MOCK_MODE) return true

  try {
    const res = await fetch(withBase(`/api/medications/${id}`), {
      method: 'DELETE',
    })
    return res.ok
  } catch {
    return false
  }
}

export async function patchMedication(
  id: string,
  done: boolean,
  voiceNote?: string,
): Promise<Medication | null> {
  if (MOCK_MODE) {
    const meds = getMockData().medications ?? []
    return meds.find((med) => med.id === id) ?? meds[0] ?? null
  }

  try {
    const res = await fetch(withBase(`/api/medications/${id}`), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ done, voice_note: voiceNote }),
    })
    if (!res.ok) return null
    return (await res.json()) as Medication
  } catch {
    return null
  }
}

export async function fetchDailyWellbeing(date?: string): Promise<DailyWellbeingEntry[] | null> {
  if (MOCK_MODE) return getMockData().daily_wellbeing ?? null

  try {
    const patientId = getPatientId()
    if (!patientId) return null
    const url = date
      ? withQuery('/api/daily-wellbeing', { target_date: date, patient_id: patientId })
      : withQuery('/api/daily-wellbeing', { patient_id: patientId })
    const res = await fetch(withBase(url))
    if (!res.ok) return null
    return (await res.json()) as DailyWellbeingEntry[]
  } catch {
    return null
  }
}

export async function postDailyWellbeing(
  payload: DailyWellbeingRequest,
): Promise<DailyWellbeingEntry | null> {
  if (MOCK_MODE) {
    const now = new Date()
    return {
      id: crypto.randomUUID(),
      patient_id: 'mock-patient',
      date: now.toISOString().slice(0, 10),
      sleep_pattern: payload.sleep_pattern,
      appetite: payload.appetite,
      mood: payload.mood,
      voice_note_id: payload.voice_note_id ?? null,
      voice_note_transcript: null,
      created_at: now.toISOString(),
    }
  }

  try {
    const patientId = getPatientId()
    if (!patientId) return null
    const res = await fetch(withBase('/api/daily-wellbeing'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...payload, patient_id: patientId }),
    })
    if (!res.ok) return null
    return (await res.json()) as DailyWellbeingEntry
  } catch {
    return null
  }
}

export async function fetchReports(): Promise<ReportSummary[] | null> {
  if (MOCK_MODE) return getMockData().reports ?? null

  try {
    const context = getReportContext()
    if (!context) return null
    const res = await fetch(
      withBase(
        withQuery('/api/reports', {
          patient_id: context.patient_id,
        }),
      ),
    )
    if (!res.ok) return null
    return (await res.json()) as ReportSummary[]
  } catch {
    return null
  }
}

export async function postReport(startDate: string, endDate: string): Promise<ReportDetail | null> {
  if (MOCK_MODE) {
    const report = getMockData().reports?.[0]
    if (!report) return null
    return {
      ...report,
      start_date: startDate,
      end_date: endDate,
      generated_at: new Date().toISOString(),
    }
  }

  try {
    const context = getReportContext()
    if (!context) return null
    const res = await fetch(withBase('/api/reports'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_date: startDate,
        end_date: endDate,
        patient_id: context.patient_id,
      }),
    })
    if (!res.ok) return null
    return (await res.json()) as ReportDetail
  } catch {
    return null
  }
}

export async function fetchReport(id: string): Promise<ReportDetail | null> {
  if (MOCK_MODE) {
    const reports = getMockData().reports ?? []
    return reports.find((report) => report.id === id) ?? null
  }

  try {
    const context = getReportContext()
    if (!context) return null
    const res = await fetch(
      withBase(
        withQuery(`/api/reports/${id}`, {
          patient_id: context.patient_id,
        }),
      ),
    )
    if (!res.ok) return null
    return (await res.json()) as ReportDetail
  } catch {
    return null
  }
}
