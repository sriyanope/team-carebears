'use client'

import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { AppLanguage } from '@/lib/api'

const STORAGE_KEY = 'pulse-language'

export const LANGUAGE_OPTIONS: Array<{ code: AppLanguage; label: string }> = [
  { code: 'en', label: 'English' },
  { code: 'zh', label: '中文' },
  { code: 'ms', label: 'Bahasa Melayu' },
  { code: 'ta', label: 'தமிழ்' },
]

interface LanguageContextValue {
  language: AppLanguage
  setLanguage: (language: AppLanguage) => void
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<AppLanguage>('en')

  useEffect(() => {
    const storedLanguage = window.localStorage.getItem(STORAGE_KEY)
    if (storedLanguage && LANGUAGE_OPTIONS.some((option) => option.code === storedLanguage)) {
      setLanguageState(storedLanguage as AppLanguage)
    }
  }, [])

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, language)
  }, [language])

  const value = useMemo(
    () => ({
      language,
      setLanguage: setLanguageState,
    }),
    [language],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}
