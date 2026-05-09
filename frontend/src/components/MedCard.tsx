'use client'

import { useEffect, useState } from 'react'
import { Medication, patchMedication, postVoiceNote } from '@/lib/api'
import { useAudioRecorder } from '@/hooks/useAudioRecorder'

interface Props {
  med: Medication
  onUpdate: (updated: Medication) => void
}

function timeBadgeStyle(med: Medication): string {
  if (med.done) return 'bg-sage-50 text-sage-500'
  const [h, m] = med.time_str.split(':').map(Number)
  const slotMs = h * 60 + m
  const nowMs = new Date().getHours() * 60 + new Date().getMinutes()
  if (nowMs > slotMs + 60) return 'bg-rose-50 text-rose-500'
  return 'bg-stone-100 text-stone-500'
}

export default function MedCard({ med, onUpdate }: Props) {
  const [recording, setRecording] = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const { isRecording, audioBlob, start, stop, reset } = useAudioRecorder()

  async function toggleDone() {
    const updated = await patchMedication(med.id, !med.done, med.voice_note_text ?? undefined)
    if (updated) onUpdate(updated)
  }

  async function handleStartRecord() {
    setRecording(true)
    await start()
  }

  function handleStopRecord() {
    stop()
  }

  useEffect(() => {
    if (!audioBlob || isRecording || !recording || transcribing) return
    async function onBlobReady() {
      if (!audioBlob) return
      setTranscribing(true)
      const note = await postVoiceNote(audioBlob, 'medication', undefined, med.id)
      if (note) {
        const updated = await patchMedication(med.id, med.done, note.transcript)
        if (updated) onUpdate(updated)
      }
      reset()
      setRecording(false)
      setTranscribing(false)
    }
    onBlobReady()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audioBlob, isRecording])

  return (
    <div className="bg-white rounded-2xl border border-stone-100 p-4 space-y-3">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleDone}
          className={`w-12 h-12 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
            med.done ? 'border-sage-500 bg-sage-50' : 'border-stone-200 bg-white'
          }`}
          style={{ minWidth: 48, minHeight: 48 }}
        >
          {med.done && <span className="text-sage-500 text-xl">✓</span>}
        </button>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-stone-900 text-lg leading-tight truncate">{med.name}</p>
          {med.note && <p className="text-stone-400 text-sm">{med.note}</p>}
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-lg flex-shrink-0 ${timeBadgeStyle(med)}`}>
          {med.time_str}
        </span>
      </div>

      <div className="border-t border-stone-100 pt-3">
        {med.voice_note_text ? (
          <div className="flex items-start gap-2">
            <p className="text-stone-600 text-sm italic flex-1 leading-relaxed">"{med.voice_note_text}"</p>
            <button
              onClick={async () => {
                const updated = await patchMedication(med.id, med.done, '')
                if (updated) onUpdate({ ...updated, voice_note_text: null })
              }}
              className="text-stone-400 text-xs px-1"
            >
              ✕
            </button>
          </div>
        ) : transcribing ? (
          <div className="flex items-center gap-2 text-stone-400 text-sm">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Transcribing…
          </div>
        ) : isRecording ? (
          <button
            onClick={handleStopRecord}
            className="w-full h-12 rounded-xl bg-rose-50 text-rose-500 text-sm font-medium"
          >
            🔴 Recording… tap to stop
          </button>
        ) : (
          <button
            onClick={handleStartRecord}
            className="w-full h-12 rounded-xl border border-dashed border-stone-200 text-stone-400 text-sm"
          >
            🎙️ Add voice observation
          </button>
        )}
      </div>
    </div>
  )
}
