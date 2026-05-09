import type { Metadata } from 'next'
import './globals.css'
import OnboardingGate from '@/components/OnboardingGate'
import { LanguageProvider } from '@/lib/LanguageContext'

export const metadata: Metadata = {
  title: 'Pulse',
  description: 'Dementia caregiver companion',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-stone-50 text-stone-700 antialiased">
        <LanguageProvider>
          <OnboardingGate>
            <div className="mx-auto min-h-screen max-w-[430px]">
              {children}
            </div>
          </OnboardingGate>
        </LanguageProvider>
      </body>
    </html>
  )
}
