'use client'

import { useEffect, useRef, useState } from 'react'
import { LANGUAGE_OPTIONS, useLanguage } from '@/lib/LanguageContext'

export default function LanguageSwitcher() {
  const { language, setLanguage, t } = useLanguage()
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const selectedLanguage = LANGUAGE_OPTIONS.find((option) => option.code === language) ?? LANGUAGE_OPTIONS[0]

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={containerRef} className="relative">
      <button
        onClick={() => setOpen((current) => !current)}
        className="flex min-h-12 items-center gap-2 rounded-2xl border border-stone-100 bg-white px-4 py-3 text-sm font-semibold text-stone-900 shadow-sm"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={t('language')}
      >
        <span>{selectedLanguage.nativeLabel}</span>
        <span className="text-stone-400">▾</span>
      </button>

      {open && (
        <div className="absolute right-0 top-full z-10 mt-2 w-44 rounded-2xl border border-stone-100 bg-white p-2 shadow-[0_12px_30px_rgba(30,28,26,0.08)]">
          <ul className="space-y-1" role="listbox" aria-label={t('language')}>
            {LANGUAGE_OPTIONS.map((option) => {
              const selected = option.code === language
              return (
                <li key={option.code}>
                  <button
                    onClick={() => {
                      setLanguage(option.code)
                      setOpen(false)
                    }}
                    className={`flex w-full items-center justify-between rounded-xl px-3 py-3 text-left text-sm ${
                      selected ? 'bg-blue-50 text-blue-700' : 'text-stone-700 hover:bg-stone-50'
                    }`}
                    role="option"
                    aria-selected={selected}
                  >
                    <span>{option.nativeLabel}</span>
                    <span className="text-xs font-semibold">{option.code.toUpperCase()}</span>
                  </button>
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </div>
  )
}
