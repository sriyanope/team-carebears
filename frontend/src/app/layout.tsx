import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SilverPulse',
  description: 'Dementia caregiver companion',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-stone-50 min-h-screen">
        <div className="mx-auto max-w-[430px] min-h-screen bg-white">
          {children}
        </div>
      </body>
    </html>
  )
}
