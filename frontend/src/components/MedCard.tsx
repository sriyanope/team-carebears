'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  CancelCircleIcon,
  CheckmarkCircle02Icon,
  Delete02Icon,
  Edit02Icon,
  Mic01Icon,
} from '@hugeicons/core-free-icons'
import AppIcon from '@/components/AppIcon'
import { deleteMedication, Medication, patchMedication, postVoiceNote } from '@/lib/api'
import { useAudioRecorder } from '@/hooks/useAudioRecorder'
import { useLanguage } from '@/lib/LanguageContext'

interface Props {
  med: Medication
  onUpdate: (updated: Medication) => void
  onDelete: (id: string) => void
}

function timeBadgeStyle(med: Medication): string {
  if (med.done) return 'bg-sage-50 text-sage-500'
  const [h, m] = med.time_str.split(':').map(Number)
  const slotMs = h * 60 + m
  const nowMs = new Date().getHours() * 60 + new Date().getMinutes()
  if (nowMs > slotMs + 60) return 'bg-rose-50 text-rose-500'
  return 'bg-stone-100 text-stone-500'
}

export default function MedCard({ med, onUpdate, onDelete }: Props) {
  const { language, t } = useLanguage()
  const [recording, setRecording] = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)
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

  async function handleDelete() {
    if (!confirmDelete) {
      setConfirmDelete(true)
      return
    }

    setDeleting(true)
    const deleted = await deleteMedication(med.id)
    setDeleting(false)
    if (deleted) onDelete(med.id)
  }

  useEffect(() => {
    if (!audioBlob || isRecording || !recording || transcribing) return
    async function onBlobReady() {
      if (!audioBlob) return
      setTranscribing(true)
      const note = await postVoiceNote(audioBlob, 'medication', language, med.id)
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
          {med.done && <AppIcon icon={CheckmarkCircle02Icon} size={24} className="text-sage-500" />}
        </button>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-stone-900 text-lg leading-tight truncate">{med.name}</p>
          {med.note && <p className="text-stone-400 text-sm">{med.note}</p>}
        </div>
        <span className={`text-xs font-medium px-2 py-1 rounded-lg flex-shrink-0 ${timeBadgeStyle(med)}`}>
          {med.time_str}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 border-t border-black border-stone-100 pt-3">
        <Link
          href={`/medications/${med.id}/edit`}
          className="flex h-12 items-center justify-center rounded-xl bg-blue-50 text-sm font-semibold text-blue-700"
        >
          <AppIcon icon={Edit02Icon} size={18} />
          Edit
        </Link>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className={`h-12 rounded-xl text-sm font-semibold ${
            confirmDelete ? 'bg-rose-50 text-rose-500' : 'bg-stone-100 text-stone-700'
          } disabled:text-stone-400`}
        >
          <span className="inline-flex items-center justify-center gap-1">
            {!deleting && !confirmDelete && <AppIcon icon={Delete02Icon} size={18} />}
            {deleting ? 'Deleting...' : confirmDelete ? 'Tap to confirm' : 'Delete'}
          </span>
        </button>
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
              <AppIcon icon={CancelCircleIcon} size={18} />
            </button>
          </div>
        ) : transcribing ? (
          <div className="flex items-center gap-2 text-stone-400 text-sm">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            {t('transcribing')}
          </div>
        ) : isRecording ? (
          <button
            onClick={handleStopRecord}
            className="w-full h-12 rounded-xl bg-rose-50 text-rose-500 text-sm font-medium"
          >
            {t('recordingTapToStop')}
          </button>
        ) : (
          <button
            onClick={handleStartRecord}
            className="w-full h-12 rounded-xl border border-dashed border-stone-200 text-stone-400 text-sm"
          >
            <span className="inline-flex items-center justify-center gap-2">
              <AppIcon icon={Mic01Icon} size={18} />
              {t('addVoiceObservation')}
            </span>
          </button>
        )}
      </div>
    </div>
  )
}
