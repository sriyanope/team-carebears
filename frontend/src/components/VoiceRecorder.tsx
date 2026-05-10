'use client'

import { useEffect, useRef, useState } from 'react'
import { Mic01Icon } from '@hugeicons/core-free-icons'
import AppIcon from '@/components/AppIcon'
import { useAudioRecorder } from '@/hooks/useAudioRecorder'
import { VoiceNote, postVoiceNote } from '@/lib/api'
import { useLanguage } from '@/lib/LanguageContext'

type RecorderState = 'idle' | 'recording' | 'transcribing' | 'review' | 'success'

interface Props {
  noteType?: string
  variant?: 'hero' | 'inline'
  idleLabel?: string
  successLabel?: string
  onSave?: (note: VoiceNote) => void
}

export default function VoiceRecorder({
  noteType = 'adhoc',
  variant = 'inline',
  idleLabel = 'Tap to record',
  successLabel = 'Saved successfully',
  onSave,
}: Props) {
  const { isRecording, audioBlob, analyserNode, duration, start, stop, reset } = useAudioRecorder()
  const { language, t } = useLanguage()
  const [state, setState] = useState<RecorderState>('idle')
  const [transcript, setTranscript] = useState('')
  const [savedNote, setSavedNote] = useState<VoiceNote | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const rafRef = useRef<number>(0)
  const successTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (isRecording) setState('recording')
  }, [isRecording])

  useEffect(() => {
    if (audioBlob && !isRecording && state === 'recording') {
      void handleTranscribe()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioBlob, isRecording])

  useEffect(() => {
    return () => {
      if (successTimeoutRef.current) clearTimeout(successTimeoutRef.current)
    }
  }, [])

  useEffect(() => {
    if (!analyserNode || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const data = new Uint8Array(analyserNode.frequencyBinCount)

    const draw = () => {
      rafRef.current = requestAnimationFrame(draw)
      analyserNode.getByteFrequencyData(data)
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      const barWidth = canvas.width / 5
      const picks = [2, 5, 10, 5, 2]

      picks.forEach((index, column) => {
        const height = Math.max(4, (data[index] / 255) * canvas.height)
        ctx.fillStyle = '#FFFFFF'
        ctx.beginPath()
        ctx.roundRect(column * barWidth + barWidth * 0.25, (canvas.height - height) / 2, barWidth * 0.5, height, 3)
        ctx.fill()
      })
    }

    draw()
    return () => cancelAnimationFrame(rafRef.current)
  }, [analyserNode])

  function handleReset() {
    if (successTimeoutRef.current) {
      clearTimeout(successTimeoutRef.current)
      successTimeoutRef.current = null
    }
    reset()
    setTranscript('')
    setSavedNote(null)
    setState('idle')
  }

  async function handleTranscribe() {
    if (!audioBlob) return

    setState('transcribing')
    const note = await postVoiceNote(audioBlob, noteType, language)

    if (!note) {
      handleReset()
      return
    }

    setSavedNote(note)
    setTranscript(note.transcript)
    setState('review')
    onSave?.(note)
  }

  function handleConfirmSave() {
    setState('success')
    successTimeoutRef.current = setTimeout(() => {
      handleReset()
    }, 1200)
  }

  const isHero = variant === 'hero'
  const heroButtonSize = 'h-56 w-56'
  const baseButtonClass = 'flex items-center justify-center text-white active:scale-[0.98] transition-transform'
  const idleButtonClass = isHero
    ? `${baseButtonClass} mx-auto rounded-full bg-blue-500 shadow-[0_18px_40px_rgba(26,111,191,0.18)]`
    : `${baseButtonClass} w-full rounded-2xl bg-blue-500 px-5 py-4`
  const recordingButtonClass = isHero
    ? `${baseButtonClass} mx-auto rounded-full bg-rose-500 shadow-[0_18px_40px_rgba(192,57,43,0.18)]`
    : `${baseButtonClass} w-full rounded-2xl bg-rose-500 px-5 py-4`
  const resolvedSuccessLabel = successLabel === 'Saved successfully' ? t('savedSuccessfully') : successLabel

  const savedAt = savedNote
    ? new Date(savedNote.created_at).toLocaleTimeString('en-SG', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      })
    : null

  if (state === 'idle') {
    return (
      <div className={isHero ? 'space-y-4 text-center' : 'space-y-3'}>
        <button onClick={() => void start()} className={isHero ? `${idleButtonClass} ${heroButtonSize}` : idleButtonClass}>
          <div className="flex flex-col items-center justify-center gap-2">
            <AppIcon icon={Mic01Icon} size={isHero ? 56 : 24} />
            <span className={`${isHero ? 'text-lg' : 'text-sm'} font-semibold`}>{idleLabel}</span>
          </div>
        </button>
      </div>
    )
  }

  if (state === 'recording') {
    const formattedDuration = `${Math.floor(duration / 60)}:${String(duration % 60).padStart(2, '0')}`

    return (
      <button
        onClick={stop}
        className={isHero ? `${recordingButtonClass} ${heroButtonSize}` : recordingButtonClass}
      >
        <div className="flex flex-col items-center justify-center gap-2">
          <canvas ref={canvasRef} width={72} height={36} className="opacity-90" />
          <span className={`${isHero ? 'text-lg' : 'text-sm'} font-semibold`}>
            {formattedDuration} · {t('tapToStop')}
          </span>
        </div>
      </button>
    )
  }

  if (state === 'transcribing') {
    return (
      <div className="space-y-3 rounded-2xl border border-blue-100 bg-blue-50 p-5 text-center">
        <div className="mx-auto h-10 w-10 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
        <p className="font-semibold text-blue-700">{t('transcribing')}</p>
        <p className="text-sm text-stone-400">{t('savingNoteIn', { language: language.toUpperCase() })}</p>
      </div>
    )
  }

  if (state === 'success') {
    return (
      <div className="space-y-2 rounded-2xl border border-sage-50 bg-sage-50 p-5 text-center">
        <p className="text-lg font-semibold text-sage-500">{t('savedCheck')}</p>
        <p className="text-sm text-stone-700">{resolvedSuccessLabel}</p>
      </div>
    )
  }

  return (
    <div className="space-y-4 rounded-2xl border border-stone-100 bg-white p-5">
      <div className="space-y-2">
        <p className="text-xs uppercase tracking-[0.18em] text-stone-400">{t('transcript')}</p>
        <p className="text-base leading-relaxed text-stone-700">{transcript}</p>
        {savedAt && <p className="text-sm text-stone-400">{t('recordedAt', { time: savedAt })}</p>}
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleReset}
          className="flex-1 rounded-xl border border-stone-100 px-4 py-3 text-sm font-medium text-stone-700"
        >
          {t('discard')}
        </button>
        <button
          onClick={handleConfirmSave}
          className="flex-1 rounded-xl bg-blue-500 px-4 py-3 text-sm font-semibold text-white"
        >
          {t('save')}
        </button>
      </div>
    </div>
  )
}
