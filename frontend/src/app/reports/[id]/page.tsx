'use client'

import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Flag01Icon } from '@hugeicons/core-free-icons'
import AppIcon from '@/components/AppIcon'
import BackButton from '@/components/BackButton'
import { ReportDetail, fetchReport } from '@/lib/api'

function formatDateRange(startDate: string, endDate: string): string {
  const start = new Intl.DateTimeFormat('en-SG', {
    day: 'numeric',
    month: 'short',
  }).format(new Date(startDate))
  const end = new Intl.DateTimeFormat('en-SG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(endDate))
  return `${start} - ${end}`
}

function formatGeneratedAt(value: string): string {
  return new Intl.DateTimeFormat('en-SG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(new Date(value))
}

const SOURCE_TYPE_LABELS: Record<string, string> = {
  voice_note: 'Voice Note',
  daily_wellbeing: 'Wellbeing',
  medication: 'Medication',
}

export default function ReportDetailPage() {
  const params = useParams<{ id: string }>()
  const reportId = Array.isArray(params.id) ? params.id[0] : params.id
  const [report, setReport] = useState<ReportDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!reportId) return
    void loadReport(reportId)
  }, [reportId])

  async function loadReport(id: string) {
    setLoading(true)
    setErrorMessage(null)
    const result = await fetchReport(id)
    if (!result) {
      setErrorMessage('Failed to load this report.')
      setLoading(false)
      return
    }
    setReport(result)
    setLoading(false)
  }

  return (
    <main className="min-h-screen bg-stone-50 px-5 py-6">
      <div className="flex items-start gap-3">
        <BackButton
          fallbackHref="/reports"
          className="mt-1 flex h-12 w-12 items-center justify-center rounded-xl bg-white text-lg text-stone-700 shadow-sm"
        />
        <div>
          <h1 className="font-serif text-3xl text-stone-900">{report?.title || 'Report'}</h1>
          {report && <p className="mt-2 text-lg text-stone-400">{formatDateRange(report.start_date, report.end_date)}</p>}
        </div>
      </div>

      {loading ? (
        <div className="flex min-h-[70vh] flex-col items-center justify-center gap-4">
          <div className="h-12 w-12 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
          <p className="text-lg text-stone-700">Loading report...</p>
        </div>
      ) : errorMessage || !report ? (
        <div className="mt-8 rounded-2xl bg-rose-50 px-5 py-4 text-lg text-rose-500">
          {errorMessage || 'Report not found.'}
        </div>
      ) : (
        <div className="mt-8 space-y-5 pb-8">
          <section className="rounded-2xl border border-stone-100 bg-white p-6 shadow-sm">
<<<<<<< Updated upstream
            <h2 className="text-2xl font-semibold text-stone-900">Summary</h2>
            <p className="mt-4 text-[20px] leading-[1.75] text-stone-700">{report.summary}</p>
          </section>

          <section className="rounded-2xl border border-stone-100 bg-white p-6 shadow-sm">
            <h2 className="flex items-center gap-2 text-2xl font-semibold text-stone-900">
              <AppIcon icon={Flag01Icon} size={24} className="text-rose-500" />
              Things to Flag
            </h2>
=======
            <h2 className="text-2xl font-semibold text-stone-900">🚩 Things to Flag</h2>
>>>>>>> Stashed changes
            {report.flags.length === 0 ? (
              <p className="mt-4 text-[20px] leading-[1.75] text-stone-700">
                Nothing specific to flag for this period.
              </p>
            ) : (
              <div className="mt-4 space-y-4">
                {report.flags.map((flag, index) => (
                  <article
                    key={`${report.id}-flag-${index}`}
                    className="rounded-2xl border border-rose-100 bg-rose-50/50 p-4"
                  >
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-rose-500">
                      What Happened
                    </p>
                    <p className="mt-2 text-base leading-7 text-stone-800">{flag.what}</p>
                    <p className="mt-4 text-xs font-semibold uppercase tracking-[0.18em] text-rose-500">
                      Why Flag This
                    </p>
                    <p className="mt-2 text-base leading-7 text-stone-700">{flag.why}</p>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-stone-100 bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold text-stone-900">Summary</h2>
            {/* <p className="mt-4 text-[19px] leading-[1.8] text-stone-700">{report.summary_narrative}</p> */}

            <div className="mt-6 space-y-4">
              {report.summary_bullets.map((bullet, index) => (
                <article
                  key={`${report.id}-summary-${index}`}
                  className="rounded-2xl border border-stone-100 bg-stone-50 p-4"
                >
                  <div className="flex items-start gap-3">
                    <span className="mt-1 text-lg text-blue-500">•</span>
                    <div className="min-w-0 flex-1">
                      <p className="text-base leading-7 text-stone-800">{bullet.text}</p>
                      {bullet.references.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {bullet.references.map((reference, referenceIndex) => (
                            <span
                              key={`${report.id}-summary-${index}-ref-${referenceIndex}`}
                              className="rounded-full bg-white px-3 py-1 text-xs font-medium text-stone-600 ring-1 ring-stone-200"
                            >
                              {reference.date_label} · {SOURCE_TYPE_LABELS[reference.source_type] ?? reference.source_type}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <p className="text-base text-stone-400">
            Generated on {formatGeneratedAt(report.generated_at)}
          </p>
        </div>
      )}
    </main>
  )
}
