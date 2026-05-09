'use client'

import Link from 'next/link'
import { useLanguage } from '@/lib/LanguageContext'

export default function ReportsPage() {
  const { t } = useLanguage()

  return (
    <main className="min-h-screen px-5 py-6">
      <div className="flex items-center gap-3">
        <Link
          href="/"
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-lg text-stone-700 shadow-sm"
        >
          ←
        </Link>
        <h1 className="font-serif text-3xl text-stone-900">{t('reports')}</h1>
      </div>

      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="rounded-2xl border border-stone-100 bg-white px-8 py-10 text-center shadow-sm">
          <p className="text-5xl">📄</p>
          <p className="mt-4 font-serif text-2xl text-stone-900">{t('reportsSoon')}</p>
        </div>
      </div>
    </main>
  )
}
