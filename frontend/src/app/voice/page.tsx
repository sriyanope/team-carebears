'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { fetchVoiceNotes, VoiceNote } from '@/lib/api'
import VoiceRecorder from '@/components/VoiceRecorder'
import NoteChip from '@/components/NoteChip'

const SLOTS = [
  { key: '9AM', label: '9 AM' },
  { key: '12PM', label: '12 PM' },
  { key: '3PM', label: '3 PM' },
  { key: '6PM', label: '6 PM' },
  { key: '9PM', label: '9 PM' },
]

const SLOT_HOURS: Record<string, number> = { '9AM': 9, '12PM': 12, '3PM': 15, '6PM': 18, '9PM': 21 }

function slotStatus(key: string, doneSlots: Set<string>): 'done' | 'current' | 'upcoming' {
  if (doneSlots.has(key)) return 'done'
  const h = new Date().getHours()
  if (h >= SLOT_HOURS[key] && h < SLOT_HOURS[key] + 3) return 'current'
  return 'upcoming'
}

const STATUS_EMOJI: Record<string, string> = { done: '✅', current: '🔴', upcoming: '⬜' }

export default function VoicePage() {
  const router = useRouter()
  const [notes, setNotes] = useState<VoiceNote[]>([])
  const [selectedSlot, setSelectedSlot] = useState<string | undefined>()

  useEffect(() => {
    fetchVoiceNotes().then((n) => { if (n) setNotes(n) })
  }, [])

  const doneSlots = new Set(notes.map((n) => n.slot).filter(Boolean) as string[])

  function handleNewNote(note: VoiceNote) {
    setNotes((prev) => [note, ...prev])
    setSelectedSlot(undefined)
  }

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
        <h1 className="text-xl font-semibold text-stone-900">Voice Notes</h1>
      </div>

      {/* Scheduled check-ins */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Scheduled check-ins</p>
        <div className="space-y-2">
          {SLOTS.map(({ key, label }) => {
            const status = slotStatus(key, doneSlots)
            return (
              <div key={key} className="bg-white rounded-2xl border border-stone-100 p-4 flex items-center gap-3">
                <span className="text-xl w-8 text-center">{STATUS_EMOJI[status]}</span>
                <div className="flex-1">
                  <p className="font-medium text-stone-900">{label}</p>
                  <p className="text-xs text-stone-400 capitalize">{status}</p>
                </div>
                {status !== 'done' && (
                  <button
                    onClick={() => setSelectedSlot(key)}
                    className={`px-4 h-10 rounded-xl text-sm font-medium transition-colors ${
                      selectedSlot === key
                        ? 'bg-blue-500 text-white'
                        : 'bg-blue-50 text-blue-500'
                    }`}
                  >
                    {selectedSlot === key ? 'Selected ✓' : 'Record'}
                  </button>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Recorder */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">
          {selectedSlot ? `Recording for ${selectedSlot}` : 'Ad-hoc note'}
        </p>
        <VoiceRecorder
          noteType={selectedSlot ? 'scheduled' : 'adhoc'}
          slot={selectedSlot}
          onSave={handleNewNote}
        />
      </div>

      {/* All notes */}
      {notes.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">
            All notes today ({notes.length})
          </p>
          <div className="space-y-2">
            {notes.map((note) => (
              <NoteChip key={note.id} note={note} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
