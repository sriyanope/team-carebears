'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { fetchTracker, postTracker, DailyLog } from '@/lib/api'
import FoodDial from '@/components/FoodDial'

const MOODS = ['😄', '🙂', '😐', '😟', '😰']
const MOOD_LABELS = ['Happy', 'Okay', 'Neutral', 'Worried', 'Distressed']

const DEMENTIA_FIELDS: Array<{ key: string; label: string; options: string[] }> = [
  { key: 'confusion', label: 'Confusion', options: ['None', 'Mild', 'Moderate', 'Severe'] },
  { key: 'agitation', label: 'Agitation', options: ['None', 'Mild', 'Moderate', 'Severe'] },
  { key: 'wandering', label: 'Wandering', options: ['No', 'Once', 'Multiple'] },
  { key: 'recognition', label: 'Recognition', options: ['Normal', 'Partial', 'Poor'] },
  { key: 'hallucinations', label: 'Hallucinations', options: ['None', 'Brief', 'Extended'] },
  { key: 'sleep_disruptions', label: 'Sleep disruptions', options: ['0', '1', '2', '3+'] },
]

interface TrackerState {
  mood: number | null
  breakfast: number
  lunch: number
  dinner: number
  hydration: number
  confusion: string
  agitation: string
  wandering: string
  recognition: string
  hallucinations: string
  sleep_disruptions: string
}

const DEFAULT_STATE: TrackerState = {
  mood: null, breakfast: 0, lunch: 0, dinner: 0, hydration: 0,
  confusion: 'None', agitation: 'None', wandering: 'No',
  recognition: 'Normal', hallucinations: 'None', sleep_disruptions: '0',
}

function fromLog(log: DailyLog): TrackerState {
  return {
    mood: log.mood,
    breakfast: log.food_breakfast,
    lunch: log.food_lunch,
    dinner: log.food_dinner,
    hydration: log.hydration,
    confusion: log.confusion,
    agitation: log.agitation,
    wandering: log.wandering,
    recognition: log.recognition,
    hallucinations: log.hallucinations,
    sleep_disruptions: String(log.sleep_disruptions),
  }
}

export default function TrackerPage() {
  const router = useRouter()
  const [state, setState] = useState<TrackerState>(DEFAULT_STATE)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10)
    fetchTracker(today).then((log) => { if (log) setState(fromLog(log)) })
  }, [])

  function update<K extends keyof TrackerState>(key: K, value: TrackerState[K]) {
    setState((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSave() {
    setSaved(true)
    await postTracker({
      mood: state.mood ?? undefined,
      food: { breakfast: state.breakfast, lunch: state.lunch, dinner: state.dinner },
      hydration: state.hydration,
      dementia_signs: {
        confusion: state.confusion,
        agitation: state.agitation,
        wandering: state.wandering,
        recognition: state.recognition,
        hallucinations: state.hallucinations,
        sleep_disruptions: state.sleep_disruptions === '3+' ? 3 : Number(state.sleep_disruptions),
      },
    })
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="px-5 py-6 space-y-6">
      {/* Top bar */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push('/')}
          className="w-10 h-10 flex items-center justify-center rounded-xl bg-stone-100 text-stone-700 text-lg"
        >
          ←
        </button>
        <h1 className="text-xl font-semibold text-stone-900">Daily Tracker</h1>
      </div>

      {/* Mood */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Mood</p>
        <div className="flex justify-between">
          {MOODS.map((emoji, i) => (
            <button
              key={i}
              onClick={() => update('mood', i)}
              className={`flex flex-col items-center gap-1 flex-1 py-3 rounded-xl transition-colors ${
                state.mood === i ? 'bg-blue-50 border-2 border-blue-500' : 'border-2 border-transparent'
              }`}
              style={{ minHeight: 48 }}
            >
              <span className="text-3xl">{emoji}</span>
              <span className="text-xs text-stone-400">{MOOD_LABELS[i]}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Food */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Food intake</p>
        <div className="bg-white rounded-2xl border border-stone-100 p-4">
          <div className="flex justify-around">
            <FoodDial label="Breakfast" value={state.breakfast} onChange={(v) => update('breakfast', v)} />
            <FoodDial label="Lunch" value={state.lunch} onChange={(v) => update('lunch', v)} />
            <FoodDial label="Dinner" value={state.dinner} onChange={(v) => update('dinner', v)} />
          </div>
        </div>
      </div>

      {/* Hydration */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Hydration</p>
        <div className="bg-white rounded-2xl border border-stone-100 p-4">
          <div className="flex justify-between mb-2">
            {Array.from({ length: 8 }, (_, i) => (
              <button
                key={i}
                onClick={() => update('hydration', i + 1 === state.hydration ? 0 : i + 1)}
                className="w-10 h-10 flex items-center justify-center rounded-xl text-2xl transition-opacity"
                style={{ opacity: i < state.hydration ? 1 : 0.25 }}
              >
                💧
              </button>
            ))}
          </div>
          <p className={`text-sm font-medium text-center ${state.hydration < 5 ? 'text-amber-500' : 'text-stone-400'}`}>
            {state.hydration}/8 glasses {state.hydration < 5 ? '· Needs more' : ''}
          </p>
        </div>
      </div>

      {/* Dementia signs */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Dementia signs</p>
        <div className="bg-white rounded-2xl border border-stone-100 p-4 grid grid-cols-2 gap-3">
          {DEMENTIA_FIELDS.map(({ key, label, options }) => (
            <div key={key}>
              <p className="text-xs text-stone-400 mb-1">{label}</p>
              <select
                value={state[key as keyof TrackerState] as string}
                onChange={(e) => update(key as keyof TrackerState, e.target.value as never)}
                className="w-full rounded-xl border border-stone-200 px-3 py-2 text-sm text-stone-700 bg-white appearance-none"
                style={{ minHeight: 44 }}
              >
                {options.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>

      {/* Save */}
      <button
        onClick={handleSave}
        className={`w-full h-14 rounded-2xl font-semibold text-base transition-colors ${
          saved ? 'bg-sage-500 text-white' : 'bg-blue-500 text-white'
        }`}
      >
        {saved ? 'Saved ✓' : 'Save log ✓'}
      </button>
    </div>
  )
}
