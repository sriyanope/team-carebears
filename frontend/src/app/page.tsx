'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ClipboardIcon, File01Icon } from '@hugeicons/core-free-icons'
import AppIcon from '@/components/AppIcon'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import VoiceRecorder from '@/components/VoiceRecorder'
import { getPatientInfo } from '@/lib/api'
import { useLanguage } from '@/lib/LanguageContext'

export default function Dashboard() {
  const { t } = useLanguage()
  const [caregiverName, setCaregiverName] = useState('Sarah')

  useEffect(() => {
    void getPatientInfo().then((info) => {
      setCaregiverName(info.caregiver_name)
    })
  }, [])

  return (
    <main className="min-h-screen px-5 py-6">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-[0.18em] text-stone-400">{t('caregiver')}</p>
          <h1 className="font-serif text-3xl leading-tight text-stone-900">
            {t('welcomeBack', { name: caregiverName })}
          </h1>
        </div>
        <LanguageSwitcher />
      </div>

      <div className="mt-8 grid grid-cols-2 gap-3">
        <Link
          href="/daily-wellbeing"
          className="flex min-h-14 items-center justify-center rounded-2xl border border-stone-100 bg-white px-4 py-4 text-center font-semibold text-stone-900 shadow-sm"
        >
          {t('dailyWellbeing')}
        </Link>
        <Link
          href="/medications"
          className="flex min-h-14 items-center justify-center rounded-2xl border border-stone-100 bg-white px-4 py-4 text-center font-semibold text-stone-900 shadow-sm"
        >
          {t('medication')}
        </Link>
      </div>

      <section className="mt-12 space-y-6">
        <div className="space-y-4 text-center">
          <p className="text-xs uppercase tracking-[0.18em] text-stone-400">{t('adhocVoiceNote')}</p>
          <div className="flex items-center justify-center gap-3">
            <div className="flex-1">
              <VoiceRecorder
                noteType="adhoc"
                variant="hero"
                idleLabel={t('tapToRecord')}
                successLabel={t('noteSaved')}
              />
            </div>
            <Link
              href="/voice-history"
              aria-label="View voice history"
              className="flex h-14 w-14 items-center justify-center self-center rounded-2xl border border-stone-100 bg-white text-stone-700 shadow-sm"
            >
              <AppIcon icon={ClipboardIcon} size={28} />
            </Link>
          </div>
        </div>

        <Link
          href="/reports"
          className="block rounded-2xl border border-stone-100 bg-white p-5 shadow-sm transition-colors hover:border-blue-100"
        >
          <p className="text-xs uppercase tracking-[0.18em] text-stone-400">{t('reports')}</p>
          <div className="mt-3 flex items-center justify-between gap-3">
            <div>
              <p className="font-serif text-2xl text-stone-900">{t('medicalSummary')}</p>
              <p className="mt-1 text-sm text-stone-400">{t('medicalSummaryDesc')}</p>
            </div>
            <span className="text-blue-500">
              <AppIcon icon={File01Icon} size={32} />
            </span>
          </div>
        </Link>
      </section>
    </main>
  )
}
