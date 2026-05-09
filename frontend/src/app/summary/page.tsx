'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { fetchSummary, SummaryResponse } from '@/lib/api'

export default function SummaryPage() {
  const router = useRouter()
  const [data, setData] = useState<SummaryResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSummary().then((d) => {
      setData(d)
      setLoading(false)
    })
  }, [])

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
        <h1 className="text-xl font-semibold text-stone-900 flex-1">Doctor Report</h1>
        <button className="px-3 h-10 rounded-xl border border-stone-200 text-stone-600 text-sm font-medium">
          📤 Export
        </button>
      </div>

      {/* AI summary banner */}
      <div className="rounded-2xl bg-blue-500 p-5 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-white text-sm font-medium opacity-80">AI Summary</span>
          <span className="text-white text-xs opacity-60 ml-auto">
            {data ? `Generated ${data.generated_at}` : 'No report yet'}
          </span>
        </div>
        {loading ? (
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <span className="text-white text-sm opacity-80">Generating…</span>
          </div>
        ) : data ? (
          <p className="text-white text-base leading-relaxed">{data.summary}</p>
        ) : (
          <p className="text-white text-base leading-relaxed">No summary available yet.</p>
        )}
      </div>

      {/* Flags */}
      {data && data.flags.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">🚩 Flag for doctor</p>
          <div className="space-y-2">
            {data.flags.map((flag, i) => (
              <div
                key={i}
                className="bg-white rounded-2xl border border-stone-100 p-4 flex gap-3"
                style={{ borderLeftWidth: 4, borderLeftColor: flag.severity === 'red' ? '#C0392B' : '#B85C00' }}
              >
                <div className="flex-1 space-y-2">
                  <p className="text-stone-700 text-sm leading-relaxed">{flag.text}</p>
                  <div className="flex flex-wrap gap-1">
                    {flag.sources.map((src) => (
                      <span key={src} className="text-xs bg-stone-100 text-stone-500 px-2 py-0.5 rounded-full">
                        {src}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Questions */}
      {data && data.questions.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-widest text-stone-400 mb-3">💬 Ask your doctor</p>
          <div className="space-y-2">
            {data.questions.map((q, i) => (
              <div key={i} className="bg-blue-50 rounded-2xl border border-blue-100 p-4 flex gap-3">
                <span className="w-7 h-7 rounded-full bg-blue-500 text-white text-sm font-semibold flex items-center justify-center flex-shrink-0">
                  {i + 1}
                </span>
                <p className="text-stone-700 text-sm leading-relaxed">{q}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Export footer */}
      <button className="w-full h-14 rounded-2xl border-2 border-stone-200 text-stone-600 font-medium text-base">
        📤 Export for Dr. Tan
      </button>
    </div>
  )
}
