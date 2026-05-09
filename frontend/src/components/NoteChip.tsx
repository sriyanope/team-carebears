import { VoiceNote } from '@/lib/api'

interface Props {
  note: VoiceNote
}

const typeStyles: Record<string, string> = {
  scheduled: 'bg-blue-50 text-blue-500',
  adhoc: 'bg-amber-50 text-amber-500',
  medication: 'bg-sage-50 text-sage-500',
}

export default function NoteChip({ note }: Props) {
  const time = new Date(note.created_at).toLocaleTimeString('en-SG', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
  const typeLabel = note.note_type === 'scheduled' ? `📅 ${note.slot || 'Scheduled'}` : note.note_type === 'medication' ? '💊 Med' : '⚡ Ad-hoc'
  const typeStyle = typeStyles[note.note_type] || typeStyles.adhoc

  return (
    <div className="bg-white rounded-2xl border border-stone-100 p-4 space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-stone-400 text-sm">{time}</span>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${typeStyle}`}>
          {typeLabel}
        </span>
        {note.severity === 'high' && (
          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-rose-50 text-rose-500 ml-auto">
            🚩 High
          </span>
        )}
      </div>
      <p className="text-stone-700 text-sm leading-relaxed line-clamp-2">{note.transcript}</p>
      {note.ai_tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {note.ai_tags.map((tag) => (
            <span key={tag} className="text-xs bg-stone-100 text-stone-600 px-2 py-0.5 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
