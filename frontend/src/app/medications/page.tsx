'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { fetchMedications, Medication } from '@/lib/api'
import MedCard from '@/components/MedCard'

const FALLBACK: Medication[] = [
  {
    id: '1', patient_id: '', name: 'Donepezil 10mg', note: "Alzheimer's · once daily",
    time_str: '08:00', done: true, voice_note_text: 'Took it without fuss this morning.',
    created_at: '', updated_at: '',
  },
  {
    id: '2', patient_id: '', name: 'Amlodipine 5mg', note: 'Blood pressure',
    time_str: '08:00', done: true, voice_note_text: null,
    created_at: '', updated_at: '',
  },
  {
    id: '3', patient_id: '', name: 'Donepezil 10mg', note: 'Evening dose',
    time_str: '21:00', done: false, voice_note_text: null,
    created_at: '', updated_at: '',
  },
]

export default function MedicationsPage() {
  const router = useRouter()
  const [meds, setMeds] = useState<Medication[]>(FALLBACK)

  useEffect(() => {
    fetchMedications().then((m) => { if (m) setMeds(m) })
  }, [])

  function handleUpdate(updated: Medication) {
    setMeds((prev) => prev.map((m) => (m.id === updated.id ? updated : m)))
  }

  const done = meds.filter((m) => m.done).length
  const allDone = done === meds.length

  return (
    <div className="px-5 py-6 space-y-5">
      {/* Top bar */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push('/')}
          className="w-10 h-10 flex items-center justify-center rounded-xl bg-stone-100 text-stone-700 text-lg"
        >
          ←
        </button>
        <h1 className="text-xl font-semibold text-stone-900 flex-1">Medications</h1>
        <span
          className={`text-sm font-semibold px-3 py-1 rounded-full ${
            allDone ? 'bg-sage-50 text-sage-500' : 'bg-blue-50 text-blue-500'
          }`}
        >
          {done}/{meds.length}
        </span>
      </div>

      {/* Med cards */}
      <div className="space-y-3">
        {meds.map((med) => (
          <MedCard key={med.id} med={med} onUpdate={handleUpdate} />
        ))}
      </div>

      {/* Footer */}
      <p className="text-xs text-stone-400 text-center leading-relaxed px-4">
        Missed doses and voice notes are included in the AI doctor report
      </p>
    </div>
  )
}
