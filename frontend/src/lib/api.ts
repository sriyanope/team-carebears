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
  try {
    const res = await fetch('/api/dashboard')
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchVoiceNotes(date?: string): Promise<VoiceNote[] | null> {
  try {
    const url = date ? `/api/voice-notes?target_date=${date}` : '/api/voice-notes'
    const res = await fetch(url)
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
  try {
    const form = new FormData()
    form.append('audio', audioBlob, 'recording.webm')
    form.append('type', type)
    if (slot) form.append('slot', slot)
    if (medId) form.append('med_id', medId)
    const res = await fetch('/api/voice-notes', { method: 'POST', body: form })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function fetchMedications(): Promise<Medication[] | null> {
  try {
    const res = await fetch('/api/medications')
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
  try {
    const res = await fetch(`/api/medications/${id}`, {
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
  try {
    const res = await fetch(`/api/tracker/${date}`)
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function postTracker(payload: TrackerPayload): Promise<DailyLog | null> {
  try {
    const res = await fetch('/api/tracker', {
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
  try {
    const res = await fetch('/api/food', {
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
  try {
    const res = await fetch('/api/hydration', {
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
  try {
    const url = date ? `/api/summary?target_date=${date}` : '/api/summary'
    const res = await fetch(url)
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}
