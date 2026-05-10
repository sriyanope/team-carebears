'use client'

import { useRouter } from 'next/navigation'

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
      ←
    </button>
  )
}
