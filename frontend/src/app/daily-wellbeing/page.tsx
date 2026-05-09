'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import VoiceRecorder from '@/components/VoiceRecorder'
import WellbeingOption from '@/components/WellbeingOption'
import { useLanguage } from '@/lib/LanguageContext'
import {
  Appetite,
  DailyWellbeingRequest,
  Mood,
  SleepPattern,
  VoiceNote,
  getPatientInfo,
  postDailyWellbeing,
} from '@/lib/api'

const sleepOptions: Array<{ value: SleepPattern; label: string; icon: string }> = [
  { value: 'earlier_sleep_later_wake', label: 'Earlier sleep time, later wake time', icon: '🌙' },
  { value: 'same', label: 'No change', icon: '=' },
  { value: 'later_sleep_earlier_wake', label: 'Later sleep time, earlier wake time', icon: '☀️' },
]

const appetiteOptions: Array<{ value: Appetite; label: string; icon: string }> = [
  { value: 'eating_less', label: 'Eating less than usual', icon: '📉' },
  { value: 'same', label: 'No change', icon: '=' },
  { value: 'eating_more', label: 'Eating more than usual', icon: '📈' },
]

const moodOptions: Array<{ value: Mood; label: string; icon: string }> = [
  { value: 'happy', label: 'Happy', icon: '😄' },
  { value: 'ok', label: 'OK', icon: '🙂' },
  { value: 'neutral', label: 'Neutral', icon: '😐' },
  { value: 'sad', label: 'Sad', icon: '😟' },
  { value: 'upset', label: 'Upset', icon: '😰' },
]

export default function DailyWellbeingPage() {
  const { t } = useLanguage()
  const [patientName, setPatientName] = useState('Dad')
  const [sleepPattern, setSleepPattern] = useState<SleepPattern | null>(null)
  const [appetite, setAppetite] = useState<Appetite | null>(null)
  const [mood, setMood] = useState<Mood | null>(null)
  const [voiceNote, setVoiceNote] = useState<VoiceNote | null>(null)
  const [saving, setSaving] = useState(false)
  const [statusMessage, setStatusMessage] = useState<string | null>(null)

  useEffect(() => {
    void getPatientInfo().then((info) => {
      setPatientName(info.patient_name)
    })
  }, [])

  const canSave = Boolean(sleepPattern && appetite && mood) && !saving

  async function handleSave() {
    if (!sleepPattern || !appetite || !mood) return

    setSaving(true)
    setStatusMessage(null)

    const payload: DailyWellbeingRequest = {
      sleep_pattern: sleepPattern,
      appetite,
      mood,
      voice_note_id: voiceNote?.id,
    }

    const result = await postDailyWellbeing(payload)
    setSaving(false)

    if (result) {
      setStatusMessage(t('dailyWellbeingSaved'))
      return
    }

    setStatusMessage(t('unableSave'))
  }

  return (
    <main className="min-h-screen px-5 py-6">
      <div className="flex items-center gap-3">
        <Link
          href="/"
          className="flex h-12 w-12 items-center justify-center rounded-xl bg-white text-lg text-stone-700 shadow-sm"
        >
          ←
        </Link>
        <h1 className="flex-1 font-serif text-3xl text-stone-900">{t('dailyWellbeing')}</h1>
        <LanguageSwitcher />
      </div>

      <div className="mt-8 space-y-8">
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-stone-900">{t('sleepQuestion')}</h2>
          <div className="grid grid-cols-3 gap-3">
            {sleepOptions.map((option) => (
              <WellbeingOption
                key={option.value}
                icon={option.icon}
                label={t(
                  option.value === 'earlier_sleep_later_wake'
                    ? 'sleepEarlier'
                    : option.value === 'later_sleep_earlier_wake'
                      ? 'sleepLater'
                      : 'sleepSame',
                )}
                selected={sleepPattern === option.value}
                onSelect={() => setSleepPattern(option.value)}
              />
            ))}
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-stone-900">{t('appetiteQuestion')}</h2>
          <div className="grid grid-cols-3 gap-3">
            {appetiteOptions.map((option) => (
              <WellbeingOption
                key={option.value}
                icon={option.icon}
                label={t(
                  option.value === 'eating_less'
                    ? 'appetiteLess'
                    : option.value === 'eating_more'
                      ? 'appetiteMore'
                      : 'appetiteSame',
                )}
                selected={appetite === option.value}
                onSelect={() => setAppetite(option.value)}
              />
            ))}
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-stone-900">{t('moodQuestion', { name: patientName })}</h2>
          <div className="grid grid-cols-5 gap-2">
            {moodOptions.map((option) => (
              <WellbeingOption
                key={option.value}
                icon={option.icon}
                label={t(
                  option.value === 'happy'
                    ? 'moodHappy'
                    : option.value === 'ok'
                      ? 'moodOk'
                      : option.value === 'neutral'
                        ? 'moodNeutral'
                        : option.value === 'sad'
                          ? 'moodSad'
                          : 'moodUpset',
                )}
                selected={mood === option.value}
                onSelect={() => setMood(option.value)}
              />
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-stone-400">{t('additionalNotes')}</p>
            <h2 className="mt-2 text-lg font-semibold text-stone-900">{t('anythingElse')}</h2>
          </div>

          <div className="rounded-2xl border border-stone-100 bg-white p-4 shadow-sm">
            <VoiceRecorder
              noteType="daily_wellbeing"
              variant="inline"
              idleLabel={t('recordOptionalNote')}
              successLabel={t('additionalNoteSaved')}
              onSave={setVoiceNote}
            />
          </div>

          {voiceNote && (
            <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
              <p className="text-sm font-semibold text-blue-700">{t('voiceNoteAttached')}</p>
              <p className="mt-2 text-sm leading-relaxed text-stone-700">{voiceNote.transcript}</p>
            </div>
          )}
        </section>
      </div>

      <div className="mt-8 space-y-3 pb-6">
        {statusMessage && (
          <div
            className={`rounded-2xl p-4 text-sm ${
              statusMessage === t('unableSave')
                ? 'bg-rose-50 text-rose-500'
                : 'bg-sage-50 text-sage-500'
            }`}
          >
            {statusMessage}
          </div>
        )}
        <button
          onClick={() => void handleSave()}
          disabled={!canSave}
          className="w-full rounded-2xl bg-blue-500 px-5 py-4 font-semibold text-white disabled:cursor-not-allowed disabled:bg-blue-100"
        >
          {saving ? t('saving') : t('save')}
        </button>
      </div>
    </main>
  )
}
