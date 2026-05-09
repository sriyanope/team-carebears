'use client'

import { useEffect, useRef, useState } from 'react'
import { useAudioRecorder } from '@/hooks/useAudioRecorder'
import { postVoiceNote, VoiceNote } from '@/lib/api'

type RecorderState = 'idle' | 'recording' | 'transcribing' | 'done'

interface Props {
  noteType?: string
  slot?: string
  compact?: boolean
  onSave?: (note: VoiceNote) => void
}

export default function VoiceRecorder({ noteType = 'adhoc', slot, compact = false, onSave }: Props) {
  const { isRecording, audioBlob, analyserNode, duration, start, stop, reset } = useAudioRecorder()
  const [state, setState] = useState<RecorderState>('idle')
  const [transcript, setTranscript] = useState('')
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const rafRef = useRef<number>(0)

  useEffect(() => {
    if (isRecording) setState('recording')
  }, [isRecording])

  useEffect(() => {
    if (audioBlob && !isRecording && state === 'recording') {
      handleTranscribe()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioBlob, isRecording])

  useEffect(() => {
    if (!analyserNode || !canvasRef.current) return
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')!
    const data = new Uint8Array(analyserNode.frequencyBinCount)

    const draw = () => {
      rafRef.current = requestAnimationFrame(draw)
      analyserNode.getByteFrequencyData(data)
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const barW = canvas.width / 5
      const picks = [2, 5, 10, 5, 2]
      picks.forEach((idx, i) => {
        const h = Math.max(4, (data[idx] / 255) * canvas.height)
        ctx.fillStyle = '#FFFFFF'
        ctx.beginPath()
        ctx.roundRect(i * barW + barW * 0.25, (canvas.height - h) / 2, barW * 0.5, h, 3)
        ctx.fill()
      })
    }
    draw()
    return () => cancelAnimationFrame(rafRef.current)
  }, [analyserNode])

  async function handleTranscribe() {
    if (!audioBlob) return
    setState('transcribing')
    const note = await postVoiceNote(audioBlob, noteType, slot)
    if (note) {
      setTranscript(note.transcript)
      setState('done')
      onSave?.(note)
    } else {
      setState('idle')
      reset()
    }
  }

  function handleDiscard() {
    reset()
    setTranscript('')
    setState('idle')
  }

  const pillHeight = compact ? 'h-12' : 'h-20'

  if (state === 'idle') {
    return (
      <button
        onClick={start}
        className={`w-full ${pillHeight} rounded-2xl bg-blue-500 flex items-center justify-center gap-3 active:scale-[0.98] transition-transform`}
      >
        <span className="text-3xl">🎙️</span>
        <span className="text-white font-semibold text-base">Tap to record</span>
      </button>
    )
  }

  if (state === 'recording') {
    const fmt = `${Math.floor(duration / 60)}:${String(duration % 60).padStart(2, '0')}`
    return (
      <button
        onClick={stop}
        className={`w-full ${pillHeight} rounded-2xl bg-rose-500 flex items-center justify-center gap-3 active:scale-[0.98] transition-transform`}
      >
        <canvas ref={canvasRef} width={60} height={32} className="opacity-90" />
        <span className="text-white font-semibold text-base">{fmt} · Tap to stop</span>
      </button>
    )
  }

  if (state === 'transcribing') {
    return (
      <div className={`w-full ${pillHeight} rounded-2xl bg-blue-500 flex items-center justify-center gap-3`}>
        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        <span className="text-white font-semibold text-base">Transcribing…</span>
      </div>
    )
  }

  return (
    <div className="rounded-2xl border border-stone-100 p-4 space-y-3">
      <p className="text-stone-700 text-sm italic leading-relaxed">{transcript}</p>
      <div className="flex gap-3">
        <button
          onClick={handleDiscard}
          className="flex-1 py-2 rounded-xl border border-stone-200 text-stone-500 text-sm font-medium"
        >
          Discard
        </button>
        <button
          onClick={() => { reset(); setState('idle') }}
          className="flex-1 py-2 rounded-xl bg-blue-500 text-white text-sm font-semibold"
        >
          Saved ✓
        </button>
      </div>
    </div>
  )
}
