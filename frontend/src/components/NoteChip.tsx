import { VoiceNote } from '@/lib/api'

interface Props {
  note: VoiceNote
}

const typeStyles: Record<string, string> = {
  adhoc: 'bg-amber-50 text-amber-500',
  daily_wellbeing: 'bg-blue-50 text-blue-500',
  medication: 'bg-stone-100 text-stone-600',
}

const typeLabels: Record<string, string> = {
  adhoc: '⚡ Ad-hoc',
  daily_wellbeing: '🌤️ Wellbeing',
  medication: '💊 Med',
}

export default function NoteChip({ note }: Props) {
  const time = new Date(note.created_at).toLocaleTimeString('en-SG', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
  const typeStyle = typeStyles[note.note_type] ?? typeStyles.adhoc
  const typeLabel = typeLabels[note.note_type] ?? '⚡ Ad-hoc'

  return (
    <div className="bg-white rounded-2xl border border-stone-100 p-4 space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-stone-400 text-sm">{time}</span>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${typeStyle}`}>
          {typeLabel}
        </span>
      </div>
      <p className="text-stone-700 text-sm leading-relaxed line-clamp-2">{note.transcript}</p>
    </div>
  )
}
