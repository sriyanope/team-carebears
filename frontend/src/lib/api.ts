export interface VoiceNote {
  id: string
  patient_id: string
  transcript: string
  note_type: string   // "adhoc" | "daily_wellbeing" | "medication"
  language: string    // "en" | "zh" | "ms" | "ta"
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

export interface DailyWellbeing {
  id: string
  patient_id: string
  date: string           // "YYYY-MM-DD"
  sleep_pattern: string  // "earlier_sleep_later_wake" | "same" | "later_sleep_earlier_wake"
  appetite: string       // "eating_less" | "same" | "eating_more"
  mood: string           // "happy" | "ok" | "neutral" | "sad" | "upset"
  voice_note_id: string | null
  created_at: string
}

export interface DailyWellbeingRequest {
  sleep_pattern: string
  appetite: string
  mood: string
  voice_note_id?: string | null
}

export interface ReportFlag {
  severity: string  // "red" | "amber"
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

interface MockData {
  voice_notes?: VoiceNote[]
  medications?: Medication[]
  daily_wellbeing?: DailyWellbeing[]
  reports?: ReportSummary[]
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

// ── Voice Notes ──────────────────────────────────────────────────────────────

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
  language: string = 'en',
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
    form.append('language', language)
    if (medId) form.append('med_id', medId)
    const res = await fetch(withBase('/api/voice-notes'), { method: 'POST', body: form })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

// ── Medications ───────────────────────────────────────────────────────────────

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
    return meds.find((m) => m.id === id) ?? meds[0] ?? null
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

// ── Daily Wellbeing ───────────────────────────────────────────────────────────

export async function fetchDailyWellbeing(date?: string): Promise<DailyWellbeing[] | null> {
  if (MOCK_MODE) return getMockData().daily_wellbeing ?? null
  try {
    const url = date ? `/api/daily-wellbeing?target_date=${date}` : '/api/daily-wellbeing'
    const res = await fetch(withBase(url))
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function postDailyWellbeing(
  payload: DailyWellbeingRequest,
): Promise<DailyWellbeing | null> {
  if (MOCK_MODE) {
    const entries = getMockData().daily_wellbeing ?? []
    return entries[0] ?? null
  }
  try {
    const res = await fetch(withBase('/api/daily-wellbeing'), {
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

// ── Reports ───────────────────────────────────────────────────────────────────

export async function fetchReports(): Promise<ReportSummary[] | null> {
  if (MOCK_MODE) return getMockData().reports ?? null
  try {
    const res = await fetch(withBase('/api/reports'))
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function postReport(
  startDate: string,
  endDate: string,
): Promise<ReportDetail | null> {
  if (MOCK_MODE) return null
  try {
    const res = await fetch(withBase('/api/reports'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_date: startDate, end_date: endDate }),
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchReport(id: string): Promise<ReportDetail | null> {
  if (MOCK_MODE) return null
  try {
    const res = await fetch(withBase(`/api/reports/${id}`))
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}
