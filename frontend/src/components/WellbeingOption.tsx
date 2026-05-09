'use client'

interface Props {
  label: string
  icon: string
  selected: boolean
  onSelect: () => void
}

export default function WellbeingOption({ label, icon, selected, onSelect }: Props) {
  return (
    <button
      onClick={onSelect}
      className={`flex min-h-16 w-full flex-col items-center justify-center rounded-xl border px-3 py-4 text-center transition-colors ${
        selected ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-stone-100 bg-white text-stone-700'
      }`}
    >
      <span className="text-3xl leading-none">{icon}</span>
      <span className="mt-2 text-sm font-medium leading-snug">{label}</span>
    </button>
  )
}
