'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import BackButton from '@/components/BackButton'
import { ReportSummary, fetchReports, postReport } from '@/lib/api'

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('en-SG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function formatGeneratedLabel(value: string): string {
  return `Generated ${formatDate(value)}`
}

function formatRange(startDate: string, endDate: string): string {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const startLabel = new Intl.DateTimeFormat('en-SG', { day: 'numeric', month: 'short' }).format(start)
  const endLabel = new Intl.DateTimeFormat('en-SG', { day: 'numeric', month: 'short', year: 'numeric' }).format(end)
  return `Data from ${startLabel} – ${endLabel}`
}

function todayString(): string {
  return new Date().toISOString().slice(0, 10)
}

function defaultStartString(): string {
  const value = new Date()
  value.setDate(value.getDate() - 7)
  return value.toISOString().slice(0, 10)
}

export default function ReportsPage() {
  const router = useRouter()
  const [reports, setReports] = useState<ReportSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [startDate, setStartDate] = useState(defaultStartString())
  const [endDate, setEndDate] = useState(todayString())

  useEffect(() => {
    void loadReports()
  }, [])

  async function loadReports() {
    setLoading(true)
    setErrorMessage(null)
    const result = await fetchReports()
    if (result === null) {
      setErrorMessage('Failed to load reports.')
      setReports([])
      setLoading(false)
      return
    }
    setReports(
      [...result].sort(
        (left, right) => new Date(right.generated_at).getTime() - new Date(left.generated_at).getTime(),
      ),
    )
    setLoading(false)
  }

  async function handleGenerateReport() {
    if (startDate > endDate) {
      setErrorMessage('Start date must be before end date.')
      return
    }

    setIsModalOpen(false)
    setGenerating(true)
    setErrorMessage(null)

    const report = await postReport(startDate, endDate)
    if (!report) {
      setGenerating(false)
      setErrorMessage('Failed to generate report. Please try again.')
      return
    }

    router.push(`/reports/${report.id}`)
  }

  return (
    <main className="min-h-screen bg-stone-50 px-5 py-6 pb-32">
      <div className="flex items-center gap-3">
        <BackButton
          fallbackHref="/"
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-lg text-stone-700 shadow-sm"
        />
        <h1 className="font-serif text-3xl text-stone-900">Reports</h1>
      </div>

      {generating ? (
        <div className="flex min-h-[70vh] flex-col items-center justify-center gap-4">
          <div className="h-12 w-12 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
          <p className="text-lg text-stone-700">Generating report...</p>
        </div>
      ) : (
        <div className="mt-8 space-y-4">
          {errorMessage && (
            <div className="rounded-2xl bg-rose-50 px-4 py-3 text-base text-rose-500">
              {errorMessage}
            </div>
          )}

          {loading ? (
            <div className="flex min-h-[40vh] flex-col items-center justify-center gap-4">
              <div className="h-10 w-10 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
              <p className="text-lg text-stone-700">Loading reports...</p>
            </div>
          ) : reports.length === 0 ? (
            <div className="rounded-2xl border border-stone-100 bg-white p-6 text-center shadow-sm">
              <p className="text-5xl">📄</p>
              <p className="mt-4 text-lg leading-relaxed text-stone-700">
                No reports yet. Create your first report below.
              </p>
            </div>
          ) : (
            reports.map((report) => (
              <button
                key={report.id}
                onClick={() => router.push(`/reports/${report.id}`)}
                className="w-full rounded-2xl border border-stone-100 bg-white p-5 text-left shadow-sm"
              >
                <p className="text-[20px] font-semibold text-stone-900">{report.title}</p>
                <p className="mt-2 text-base text-stone-400">{formatGeneratedLabel(report.generated_at)}</p>
                <p className="mt-1 text-base text-stone-400">{formatRange(report.start_date, report.end_date)}</p>
              </button>
            ))
          )}
        </div>
      )}

      {!generating && (
        <div className="fixed bottom-0 left-1/2 w-full max-w-[430px] -translate-x-1/2 bg-gradient-to-t from-stone-50 via-stone-50 to-transparent px-5 pb-6 pt-8">
          <button
            onClick={() => {
              setErrorMessage(null)
              setIsModalOpen(true)
            }}
            className="w-full rounded-2xl bg-blue-500 px-5 py-4 text-lg font-semibold text-white shadow-sm"
          >
            + Create New Report
          </button>
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-stone-900/30 px-5">
          <div className="w-full max-w-[380px] rounded-2xl bg-white p-6 shadow-[0_18px_45px_rgba(30,28,26,0.16)]">
            <h2 className="font-serif text-2xl text-stone-900">Select Date Range</h2>

            <div className="mt-5 space-y-4">
              <label className="block">
                <span className="mb-2 block text-base font-medium text-stone-700">Start date</span>
                <input
                  type="date"
                  value={startDate}
                  onChange={(event) => setStartDate(event.target.value)}
                  className="min-h-12 w-full rounded-xl border border-stone-100 bg-stone-50 px-4 text-base text-stone-900"
                />
              </label>

              <label className="block">
                <span className="mb-2 block text-base font-medium text-stone-700">End date</span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(event) => setEndDate(event.target.value)}
                  className="min-h-12 w-full rounded-xl border border-stone-100 bg-stone-50 px-4 text-base text-stone-900"
                />
              </label>
            </div>

            <div className="mt-6 space-y-3">
              <button
                onClick={() => void handleGenerateReport()}
                className="w-full rounded-2xl bg-blue-500 px-5 py-4 text-lg font-semibold text-white"
              >
                Generate Report
              </button>
              <button
                onClick={() => setIsModalOpen(false)}
                className="w-full rounded-2xl border border-stone-100 px-5 py-4 text-lg font-medium text-stone-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
