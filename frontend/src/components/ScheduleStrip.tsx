import { ScheduleSlot } from '@/lib/api'

interface Props {
  slots: ScheduleSlot[]
}

const STATUS_ICON: Record<string, string> = {
  done: '✅',
  current: '🔴',
  upcoming: '⬜',
}

export default function ScheduleStrip({ slots }: Props) {
  return (
    <div className="flex items-end justify-between px-2">
      {slots.map((slot, i) => (
        <div key={slot.slot} className="flex flex-col items-center gap-1 flex-1">
          <span className="text-lg leading-none">{STATUS_ICON[slot.status]}</span>
          <span className={`text-xs font-medium ${slot.status === 'current' ? 'text-blue-500' : 'text-stone-400'}`}>
            {slot.label}
          </span>
          {i < slots.length - 1 && (
            <div className="absolute" />
          )}
        </div>
      ))}
    </div>
  )
}
