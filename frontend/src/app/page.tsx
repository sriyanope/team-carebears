'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { fetchVoiceNotes, fetchMedications, VoiceNote, Medication } from '@/lib/api'
import VoiceRecorder from '@/components/VoiceRecorder'
import NoteChip from '@/components/NoteChip'

function greeting(): string {
  const h = new Date().getHours()
  const time = h < 12 ? 'morning' : h < 17 ? 'afternoon' : 'evening'
  return `Good ${time}`
}

export default function Dashboard() {
  const [notes, setNotes] = useState<VoiceNote[]>([])
  const [meds, setMeds] = useState<Medication[]>([])

  useEffect(() => {
    fetchVoiceNotes().then((n) => { if (n) setNotes(n) })
    fetchMedications().then((m: Medication[] | null) => { if (m) setMeds(m) })
  }, [])

  function handleNewNote(note: VoiceNote) {
    setNotes((prev) => [note, ...prev])
  }

  const medsDone = meds.filter((m) => m.done).length
  const today = new Date().toLocaleDateString('en-SG', { weekday: 'long', day: 'numeric', month: 'long' })

  return (
    <div className="px-5 py-6 space-y-6">
      {/* Header */}
      <div>
        <p className="text-xs text-stone-400">{today}</p>
        <h1 className="text-xl font-semibold text-stone-900 mt-0.5">{greeting()} 👋</h1>
      </div>

      {/* Nav buttons */}
      <div className="grid grid-cols-2 gap-3">
        <Link
          href="/daily-wellbeing"
          className="bg-white rounded-2xl border border-stone-100 p-4 space-y-1 active:scale-[0.97] transition-transform"
        >
          <span className="text-3xl">🌤️</span>
          <p className="font-semibold text-stone-900 text-base mt-1">Daily Wellbeing</p>
          <p className="text-stone-400 text-xs leading-snug">Sleep, appetite &amp; mood</p>
        </Link>
        <Link
          href="/medications"
          className="bg-white rounded-2xl border border-stone-100 p-4 space-y-1 active:scale-[0.97] transition-transform"
        >
          <span className="text-3xl">💊</span>
          <p className="font-semibold text-stone-900 text-base mt-1">Medication</p>
          <p className="text-stone-400 text-xs leading-snug">
            {meds.length > 0 ? `${medsDone}/${meds.length} done` : 'Track doses'}
          </p>
        </Link>
      </div>

      {/* Voice Recorder */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Ad-hoc note</p>
        <VoiceRecorder noteType="adhoc" onSave={handleNewNote} />
      </div>

      {/* Actions row */}
      <div className="flex gap-3">
        <Link
          href="/voice"
          className="flex-1 py-3 rounded-2xl bg-stone-100 text-stone-700 text-sm font-medium text-center active:scale-[0.97] transition-transform"
        >
          🕑 Voice History
        </Link>
        <Link
          href="/reports"
          className="flex-1 py-3 rounded-2xl bg-blue-500 text-white text-sm font-semibold text-center active:scale-[0.97] transition-transform"
        >
          🏥 Medical Summary
        </Link>
      </div>

      {/* Recent notes */}
      {notes.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Recent notes</p>
          <div className="space-y-2">
            {notes.slice(0, 3).map((note: VoiceNote) => (
              <NoteChip key={note.id} note={note} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
