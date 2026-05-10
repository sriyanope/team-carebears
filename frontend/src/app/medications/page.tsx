'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { fetchMedications, Medication } from '@/lib/api'
import MedCard from '@/components/MedCard'
import { useLanguage } from '@/lib/LanguageContext'

export default function MedicationsPage() {
  const router = useRouter()
  const { t } = useLanguage()
  const [meds, setMeds] = useState<Medication[] | null>(null)

  useEffect(() => {
    fetchMedications().then((m) => { if (m) setMeds(m) })
  }, [])

  function handleUpdate(updated: Medication) {
    setMeds((prev) => (prev ? prev.map((m) => (m.id === updated.id ? updated : m)) : prev))
  }

  function handleDelete(id: string) {
    setMeds((prev) => (prev ? prev.filter((m) => m.id !== id) : prev))
  }

  if (!meds) {
    return (
      <div className="px-5 py-6 text-stone-400 text-sm">
        {t('noData')}
      </div>
    )
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
          &larr;
        </button>
        <h1 className="text-xl font-semibold text-stone-900 flex-1">{t('medication')}</h1>
        <span
          className={`text-sm font-semibold px-3 py-1 rounded-full ${
            allDone ? 'bg-sage-50 text-sage-500' : 'bg-blue-50 text-blue-500'
          }`}
        >
          {done}/{meds.length}
        </span>
      </div>

      <Link
        href="/medications/add"
        className="flex min-h-14 items-center justify-center gap-2 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-4 text-lg font-semibold text-blue-700 active:scale-[0.99]"
      >
        <span className="text-2xl">+</span>
        Add new medication
      </Link>

      {/* Med cards */}
      <div className="space-y-3">
        {meds.map((med) => (
          <MedCard key={med.id} med={med} onUpdate={handleUpdate} onDelete={handleDelete} />
        ))}
      </div>

      {/* Footer */}
      <p className="text-xs text-stone-400 text-center leading-relaxed px-4">
        {t('medsFooter')}
      </p>
    </div>
  )
}
