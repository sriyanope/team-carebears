'use client'

import { useRouter } from 'next/navigation'
import { ArrowLeft01Icon } from '@hugeicons/core-free-icons'
import AppIcon from '@/components/AppIcon'

interface BackButtonProps {
  fallbackHref: string
  className?: string
}

export default function BackButton({ fallbackHref, className }: BackButtonProps) {
  const router = useRouter()

  function handleClick() {
    if (typeof window !== 'undefined' && window.history.length > 1) {
      router.back()
      return
    }

    router.push(fallbackHref)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label="Go back"
      className={className}
    >
      <AppIcon icon={ArrowLeft01Icon} size={22} />
    </button>
  )
}
