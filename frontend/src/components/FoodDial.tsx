'use client'

import { useEffect, useRef, useCallback } from 'react'

const SNAPS = [0, 25, 50, 75, 100]
const EMOJI = ['🚫', '🍽️', '🥣', '🥘', '✅']

interface Props {
  label: string
  value: number
  onChange: (v: number) => void
}

function snap(v: number): number {
  return SNAPS.reduce((a, b) => (Math.abs(b - v) < Math.abs(a - v) ? b : a))
}

export default function FoodDial({ label, value, onChange }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const dragging = useRef(false)

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')!
    const cx = canvas.width / 2
    const cy = canvas.height / 2
    const r = cx - 6
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // track
    ctx.beginPath()
    ctx.arc(cx, cy, r, 0, Math.PI * 2)
    ctx.strokeStyle = '#E8F2FB'
    ctx.lineWidth = 8
    ctx.stroke()

    // arc
    const pct = value / 100
    const start = -Math.PI / 2
    const end = start + pct * Math.PI * 2
    ctx.beginPath()
    ctx.arc(cx, cy, r, start, end)
    ctx.strokeStyle = value < 50 ? '#B85C00' : '#1A6FBF'
    ctx.lineWidth = 8
    ctx.lineCap = 'round'
    ctx.stroke()
  }, [value])

  useEffect(() => { draw() }, [draw])

  function angleToValue(canvas: HTMLCanvasElement, clientX: number, clientY: number): number {
    const rect = canvas.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    const angle = Math.atan2(clientY - cy, clientX - cx)
    const deg = ((angle * 180) / Math.PI + 90 + 360) % 360
    return snap((deg / 360) * 100)
  }

  function onPointerDown(e: React.PointerEvent<HTMLCanvasElement>) {
    dragging.current = true
    canvasRef.current?.setPointerCapture(e.pointerId)
  }

  function onPointerMove(e: React.PointerEvent<HTMLCanvasElement>) {
    if (!dragging.current || !canvasRef.current) return
    onChange(angleToValue(canvasRef.current, e.clientX, e.clientY))
  }

  function onPointerUp() {
    dragging.current = false
  }

  const emojiIdx = SNAPS.indexOf(value)
  const emoji = emojiIdx >= 0 ? EMOJI[emojiIdx] : '🍽️'

  return (
    <div className="flex flex-col items-center gap-1">
      <span className="text-xl">{emoji}</span>
      <span className="text-xs uppercase tracking-widest text-stone-400">{label}</span>
      <canvas
        ref={canvasRef}
        width={80}
        height={80}
        className="cursor-pointer touch-none"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
      />
      <span
        className="font-serif text-2xl leading-none"
        style={{ color: value < 50 ? '#B85C00' : '#1A6FBF' }}
      >
        {value}%
      </span>
    </div>
  )
}
