'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { VoiceNote, fetchVoiceNotes } from '@/lib/api'
import { TranslationKey, useLanguage } from '@/lib/LanguageContext'

const sourceLabelKeys: Record<string, TranslationKey> = {
  adhoc: 'adhoc',
  daily_wellbeing: 'dailyWellbeing',
  medication: 'medication',
}

function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat('en-SG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(new Date(value))
}

export default function VoiceHistoryPage() {
  const { t } = useLanguage()
  const [notes, setNotes] = useState<VoiceNote[]>([])

  useEffect(() => {
    void fetchVoiceNotes().then((result) => {
      const items = result ?? []
      const sorted = [...items].sort(
        (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime(),
      )
      setNotes(sorted)
    })
  }, [])

  return (
    <main className="min-h-screen px-5 py-6">
      <div className="flex items-center gap-3">
        <Link
          href="/"
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-lg text-stone-700 shadow-sm"
        >
          ←
        </Link>
        <h1 className="font-serif text-3xl text-stone-900">{t('voiceHistory')}</h1>
      </div>

      <div className="mt-8 space-y-4 pb-6">
        {notes.length === 0 ? (
          <div className="rounded-2xl border border-stone-100 bg-white p-6 text-center shadow-sm">
            <p className="text-xl">🎙️</p>
            <p className="mt-3 text-base text-stone-700">
              {t('noVoiceNotesYet')}
            </p>
          </div>
        ) : (
          notes.map((note) => (
            <article key={note.id} className="rounded-2xl border border-stone-100 bg-white p-5 shadow-sm">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-sm text-stone-400">{formatTimestamp(note.created_at)}</p>
                <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-medium text-blue-500">
                  {t(sourceLabelKeys[note.note_type] ?? 'adhoc')}
                </span>
              </div>
              <p className="mt-4 whitespace-pre-wrap text-base leading-relaxed text-stone-700">{note.transcript}</p>
            </article>
          ))
        )}
      </div>
    </main>
  )
}
