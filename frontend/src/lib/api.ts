export interface VoiceNote {
  id: string
  patient_id: string
  transcript: string
  categories: string[]
  ai_tags: string[]
  severity: string
  note_type: string
  slot: string | null
  med_id: string | null
  created_at: string
  updated_at: string
}

export interface Medication {
  id: string
  patient_id: string
  name: string
  note: string | null
  time_str: string
  done: boolean
  voice_note_text: string | null
  created_at: string
  updated_at: string
}

export interface DailyLog {
  id: string
  patient_id: string
  date: string
  mood: number | null
  food_breakfast: number
  food_lunch: number
  food_dinner: number
  hydration: number
  confusion: string
  agitation: string
  wandering: string
  recognition: string
  hallucinations: string
  sleep_disruptions: number
  created_at: string
  updated_at: string
}

export interface ScheduleSlot {
  slot: string
  label: string
  status: 'done' | 'current' | 'upcoming'
}

export interface PatientInfo {
  name: string
  caregiver_name: string
  tracking_days: number
}

export interface DashboardMetrics {
  meds_done: number
  meds_total: number
  food_avg: number
  hydration: number
  notes_count: number
}

export interface DashboardResponse {
  patient: PatientInfo
  metrics: DashboardMetrics
  schedule: ScheduleSlot[]
  recent_notes: VoiceNote[]
}

export interface Flag {
  severity: string
  text: string
  sources: string[]
}

export interface SummaryResponse {
  summary: string
  generated_at: string
  flags: Flag[]
  questions: string[]
}

interface MockData {
  dashboard?: DashboardResponse
  voice_notes?: VoiceNote[]
  medications?: Medication[]
  daily_log?: DailyLog
  summary?: SummaryResponse
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

export interface TrackerPayload {
  mood?: number
  food?: { breakfast?: number; lunch?: number; dinner?: number }
  hydration?: number
  dementia_signs?: {
    confusion: string
    agitation: string
    wandering: string
    recognition: string
    hallucinations: string
    sleep_disruptions: number
  }
}

export async function fetchDashboard(): Promise<DashboardResponse | null> {
  if (MOCK_MODE) return getMockData().dashboard ?? null
  try {
    const res = await fetch(withBase('/api/dashboard'))
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchVoiceNotes(date?: string): Promise<VoiceNote[] | null> {
  if (MOCK_MODE) return getMockData().voice_notes ?? null
  try {
    const url = date ? `/api/voice-notes?target_date=${date}` : '/api/voice-notes'
    const res = await fetch(withBase(url))
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function postVoiceNote(
  audioBlob: Blob,
  type: string,
  slot?: string,
  medId?: string,
): Promise<VoiceNote | null> {
  if (MOCK_MODE) {
    const notes = getMockData().voice_notes ?? []
    return notes[0] ?? null
  }
  try {
    const form = new FormData()
    form.append('audio', audioBlob, 'recording.webm')
    form.append('type', type)
    if (slot) form.append('slot', slot)
    if (medId) form.append('med_id', medId)
    const res = await fetch(withBase('/api/voice-notes'), { method: 'POST', body: form })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchMedications(): Promise<Medication[] | null> {
  if (MOCK_MODE) return getMockData().medications ?? null
  try {
    const res = await fetch(withBase('/api/medications'))
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function patchMedication(
  id: string,
  done: boolean,
  voiceNote?: string,
): Promise<Medication | null> {
  if (MOCK_MODE) {
    const meds = getMockData().medications ?? []
    const found = meds.find((m) => m.id === id)
    return found ?? meds[0] ?? null
  }
  try {
    const res = await fetch(withBase(`/api/medications/${id}`), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ done, voice_note: voiceNote }),
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchTracker(date: string): Promise<DailyLog | null> {
  if (MOCK_MODE) return getMockData().daily_log ?? null
  try {
    const res = await fetch(withBase(`/api/tracker/${date}`))
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function postTracker(payload: TrackerPayload): Promise<DailyLog | null> {
  if (MOCK_MODE) return getMockData().daily_log ?? null
  try {
    const res = await fetch(withBase('/api/tracker'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function patchFood(breakfast?: number, lunch?: number, dinner?: number): Promise<DailyLog | null> {
  if (MOCK_MODE) return getMockData().daily_log ?? null
  try {
    const res = await fetch(withBase('/api/food'), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ breakfast, lunch, dinner }),
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function patchHydration(glasses: number): Promise<DailyLog | null> {
  if (MOCK_MODE) return getMockData().daily_log ?? null
  try {
    const res = await fetch(withBase('/api/hydration'), {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ glasses }),
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchSummary(date?: string): Promise<SummaryResponse | null> {
  if (MOCK_MODE) return getMockData().summary ?? null
  try {
    const url = date ? `/api/summary?target_date=${date}` : '/api/summary'
    const res = await fetch(withBase(url))
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}
