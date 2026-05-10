'use client'

import { HugeiconsIcon } from '@hugeicons/react'
import type { IconSvgElement } from '@hugeicons/react'

interface AppIconProps {
  icon: IconSvgElement
  size?: number
  className?: string
  strokeWidth?: number
  title?: string
}

export default function AppIcon({
  icon,
  size = 24,
  className,
  strokeWidth = 1.8,
  title,
}: AppIconProps) {
  return (
    <HugeiconsIcon
      icon={icon}
      size={size}
      color="currentColor"
      strokeWidth={strokeWidth}
      className={className}
      aria-hidden={title ? undefined : true}
      aria-label={title}
      role={title ? 'img' : undefined}
    />
  )
}
