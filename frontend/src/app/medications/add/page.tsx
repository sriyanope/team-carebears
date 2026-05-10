'use client'

import { FormEvent, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { postMedication } from '@/lib/api'

export default function AddMedicationPage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [dosage, setDosage] = useState('')
  const [frequencyPerWeek, setFrequencyPerWeek] = useState('7')
  const [specialInstructions, setSpecialInstructions] = useState('')
  const [expiryDate, setExpiryDate] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canSave = name.trim() && dosage.trim() && Number(frequencyPerWeek) > 0 && !saving

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!canSave) return

    setSaving(true)
    setError(null)

    const medication = await postMedication({
      name: name.trim(),
      dosage: dosage.trim(),
      frequency_per_week: Number(frequencyPerWeek),
      special_instructions: specialInstructions.trim() || undefined,
      expiry_date: expiryDate || undefined,
    })

    setSaving(false)

    if (!medication) {
      setError('Unable to add this medication right now. Please try again.')
      return
    }

    router.push('/medications')
  }

  return (
    <main className="min-h-screen bg-stone-50 px-5 py-6">
      <div className="flex items-center gap-3">
        <Link
          href="/medications"
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-lg text-stone-700 shadow-sm"
          aria-label="Back to medication list"
        >
          &larr;
        </Link>
        <div className="flex-1">
          <p className="text-xs uppercase tracking-[0.18em] text-stone-400">Medication</p>
          <h1 className="font-serif text-3xl leading-tight text-stone-900">Add medicine</h1>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4 pb-6">
        <div className="rounded-2xl border border-stone-100 bg-white p-4 shadow-sm">
          <label className="block">
            <span className="mb-3 flex items-center gap-3 text-lg font-semibold text-stone-900">
              <span className="text-3xl">{'\uD83D\uDC8A'}</span>
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
              <span className="text-3xl">{'\uD83D\uDCDD'}</span>
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
              <span className="text-3xl">{'\uD83D\uDCC5'}</span>
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
          {saving ? 'Adding...' : 'Add medication'}
        </button>
      </form>
    </main>
  )
}
