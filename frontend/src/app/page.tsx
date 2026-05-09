'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { fetchDashboard, DashboardResponse, VoiceNote } from '@/lib/api'
import MetricCard from '@/components/MetricCard'
import ScheduleStrip from '@/components/ScheduleStrip'
import VoiceRecorder from '@/components/VoiceRecorder'
import NoteChip from '@/components/NoteChip'
import { ScheduleSlot } from '@/lib/api'

const FALLBACK: DashboardResponse = {
  patient: { name: 'Dad', caregiver_name: 'Sarah', tracking_days: 1 },
  metrics: { meds_done: 2, meds_total: 3, food_avg: 42, hydration: 3, notes_count: 3 },
  schedule: [
    { slot: '9AM', label: '9 AM', status: 'done' },
    { slot: '12PM', label: '12 PM', status: 'done' },
    { slot: '3PM', label: '3 PM', status: 'current' },
    { slot: '6PM', label: '6 PM', status: 'upcoming' },
    { slot: '9PM', label: '9 PM', status: 'upcoming' },
  ] as ScheduleSlot[],
  recent_notes: [],
}

const NAV = [
  { href: '/medications', emoji: '💊', title: 'Medications', desc: 'Track doses & observations' },
  { href: '/voice', emoji: '🎙️', title: 'Voice Notes', desc: 'Scheduled & ad-hoc logs' },
  { href: '/tracker', emoji: '📊', title: 'Daily Tracker', desc: 'Food, mood, hydration' },
  { href: '/summary', emoji: '🏥', title: 'Doctor Report', desc: 'AI-generated summary' },
]

function greeting(name: string): string {
  const h = new Date().getHours()
  const time = h < 12 ? 'morning' : h < 17 ? 'afternoon' : 'evening'
  return `Good ${time}, ${name} 👋`
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardResponse>(FALLBACK)
  const [notes, setNotes] = useState<VoiceNote[]>([])

  useEffect(() => {
    fetchDashboard().then((d) => {
      if (d) {
        setData(d)
        setNotes(d.recent_notes)
      }
    })
  }, [])

  function handleNewNote(note: VoiceNote) {
    setNotes((prev) => [note, ...prev])
    setData((prev) => ({
      ...prev,
      metrics: { ...prev.metrics, notes_count: prev.metrics.notes_count + 1 },
    }))
  }

  const { patient, metrics, schedule } = data
  const today = new Date().toLocaleDateString('en-SG', { weekday: 'long', day: 'numeric', month: 'long' })
  const foodVariant = metrics.food_avg < 60 ? 'warning' : 'default'
  const hydrationVariant = metrics.hydration < 5 ? 'warning' : 'default'
  const medVariant = metrics.meds_done === metrics.meds_total ? 'success' : 'default'

  return (
    <div className="px-5 py-6 space-y-5">
      {/* Header */}
      <div>
        <p className="text-xs text-stone-400">{today}</p>
        <h1 className="text-xl font-semibold text-stone-900 mt-0.5">{greeting(patient.caregiver_name)}</h1>
        <p className="text-stone-400 text-sm mt-0.5">{patient.name} · Day {patient.tracking_days}</p>
      </div>

      {/* Voice Recorder */}
      <VoiceRecorder noteType="adhoc" onSave={handleNewNote} />

      {/* Metrics */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Today at a glance</p>
        <div className="grid grid-cols-2 gap-3">
          <MetricCard
            emoji="💊"
            label="Meds"
            value={`${metrics.meds_done}/${metrics.meds_total}`}
            sub={metrics.meds_done === metrics.meds_total ? 'All done ✓' : `${metrics.meds_total - metrics.meds_done} remaining`}
            variant={medVariant}
          />
          <MetricCard
            emoji="🍽️"
            label="Food"
            value={`${metrics.food_avg}%`}
            sub={metrics.food_avg < 60 ? 'Below target' : 'On track'}
            variant={foodVariant}
          />
          <MetricCard
            emoji="💧"
            label="Hydration"
            value={`${metrics.hydration}/8`}
            sub={metrics.hydration < 5 ? 'Needs attention' : 'Good'}
            variant={hydrationVariant}
          />
          <MetricCard
            emoji="🎙️"
            label="Notes"
            value={String(metrics.notes_count)}
            sub="logged today"
          />
        </div>
      </div>

      {/* Schedule */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Check-ins</p>
        <div className="bg-blue-50 rounded-2xl border border-blue-100 p-4">
          <ScheduleStrip slots={schedule} />
        </div>
      </div>

      {/* Nav cards */}
      <div>
        <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Quick access</p>
        <div className="grid grid-cols-2 gap-3">
          {NAV.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className="bg-white rounded-2xl border border-stone-100 p-4 space-y-1 active:scale-[0.97] transition-transform"
            >
              <span className="text-3xl">{n.emoji}</span>
              <p className="font-semibold text-stone-900 text-base mt-1">{n.title}</p>
              <p className="text-stone-400 text-xs leading-snug">{n.desc}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* Notes list */}
      {notes.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">Today's notes</p>
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
