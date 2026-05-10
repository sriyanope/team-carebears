'use client'

import { FormEvent, useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import {
  ArrowLeft01Icon,
  Calendar03Icon,
  Medicine01Icon,
  StickyNote01Icon,
} from '@hugeicons/core-free-icons'
import AppIcon from '@/components/AppIcon'
import { fetchMedication, updateMedicationDetails } from '@/lib/api'

export default function EditMedicationPage() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const [name, setName] = useState('')
  const [dosage, setDosage] = useState('')
  const [frequencyPerWeek, setFrequencyPerWeek] = useState('7')
  const [specialInstructions, setSpecialInstructions] = useState('')
  const [expiryDate, setExpiryDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void fetchMedication(params.id).then((medication) => {
      if (!medication) {
        setError('Medication not found.')
        setLoading(false)
        return
      }

      setName(medication.name)
      setDosage(medication.dosage ?? '')
      setFrequencyPerWeek(String(medication.frequency_per_week ?? 7))
      setSpecialInstructions(medication.special_instructions ?? '')
      setExpiryDate(medication.expiry_date ?? '')
      setLoading(false)
    })
  }, [params.id])

  const canSave = name.trim() && dosage.trim() && Number(frequencyPerWeek) > 0 && !saving

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!canSave) return

    setSaving(true)
    setError(null)

    const medication = await updateMedicationDetails(params.id, {
      name: name.trim(),
      dosage: dosage.trim(),
      frequency_per_week: Number(frequencyPerWeek),
      special_instructions: specialInstructions.trim() || null,
      expiry_date: expiryDate || null,
    })

    setSaving(false)

    if (!medication) {
      setError('Unable to update this medication right now. Please try again.')
      return
    }

    router.push('/medications')
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-stone-50 px-5 py-6 text-sm text-stone-400">
        Loading medication...
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-stone-50 px-5 py-6">
      <div className="flex items-center gap-3">
        <Link
          href="/medications"
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-lg text-stone-700 shadow-sm"
          aria-label="Back to medication list"
        >
          <AppIcon icon={ArrowLeft01Icon} size={22} />
        </Link>
        <div className="flex-1">
          <p className="text-xs uppercase tracking-[0.18em] text-stone-400">Medication</p>
          <h1 className="font-serif text-3xl leading-tight text-stone-900">Edit medicine</h1>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4 pb-6">
        <div className="rounded-2xl border border-stone-100 bg-white p-4 shadow-sm">
          <label className="block">
            <span className="mb-3 flex items-center gap-3 text-lg font-semibold text-stone-900">
              <AppIcon icon={Medicine01Icon} size={28} className="text-blue-500" />
              Name of medicine
            </span>
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="min-h-14 w-full rounded-2xl border border-stone-100 bg-stone-50 px-4 text-lg text-stone-900 outline-none focus:border-blue-500"
              placeholder="e.g. Amlodipine"
              autoComplete="off"
            />
          </label>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-2xl border border-stone-100 bg-white p-4 shadow-sm">
            <label className="block">
              <span className="mb-3 block text-lg font-semibold text-stone-900">Dosage</span>
              <input
                value={dosage}
                onChange={(event) => setDosage(event.target.value)}
                className="min-h-14 w-full rounded-2xl border border-stone-100 bg-stone-50 px-4 text-lg text-stone-900 outline-none focus:border-blue-500"
                placeholder="10mg"
                autoComplete="off"
              />
            </label>
          </div>

          <div className="rounded-2xl border border-stone-100 bg-white p-4 shadow-sm">
            <label className="block">
              <span className="mb-3 block text-lg font-semibold text-stone-900">Times/week</span>
              <input
                value={frequencyPerWeek}
                onChange={(event) => setFrequencyPerWeek(event.target.value)}
                className="min-h-14 w-full rounded-2xl border border-stone-100 bg-stone-50 px-4 text-lg text-stone-900 outline-none focus:border-blue-500"
                type="number"
                inputMode="numeric"
                min="1"
                max="21"
              />
            </label>
          </div>
        </div>

        <div className="rounded-2xl border border-stone-100 bg-white p-4 shadow-sm">
          <label className="block">
            <span className="mb-3 flex items-center gap-3 text-lg font-semibold text-stone-900">
              <AppIcon icon={StickyNote01Icon} size={28} className="text-blue-500" />
              Special instructions
            </span>
            <textarea
              value={specialInstructions}
              onChange={(event) => setSpecialInstructions(event.target.value)}
              className="min-h-28 w-full resize-none rounded-2xl border border-stone-100 bg-stone-50 px-4 py-3 text-lg text-stone-900 outline-none focus:border-blue-500"
              placeholder="e.g. Take after breakfast. Watch for dizziness."
            />
          </label>
        </div>

        <div className="rounded-2xl border border-stone-100 bg-white p-4 shadow-sm">
          <label className="block">
            <span className="mb-3 flex items-center gap-3 text-lg font-semibold text-stone-900">
              <AppIcon icon={Calendar03Icon} size={28} className="text-blue-500" />
              Date of expiry
            </span>
            <input
              value={expiryDate}
              onChange={(event) => setExpiryDate(event.target.value)}
              className="min-h-14 w-full rounded-2xl border border-stone-100 bg-stone-50 px-4 text-lg text-stone-900 outline-none focus:border-blue-500"
              type="date"
            />
          </label>
        </div>

        {error && (
          <div className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-500">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={!canSave}
          className="min-h-14 w-full rounded-2xl bg-blue-500 px-5 py-4 text-lg font-semibold text-white active:scale-[0.99] disabled:bg-stone-100 disabled:text-stone-400"
        >
          {saving ? 'Saving...' : 'Save medication'}
        </button>
      </form>
    </main>
  )
}
