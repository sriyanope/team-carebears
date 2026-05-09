interface Props {
  emoji: string
  label: string
  value: string
  sub: string
  variant?: 'default' | 'warning' | 'alert' | 'success'
}

const variantStyles: Record<string, { bg: string; subColor: string }> = {
  default: { bg: 'bg-white', subColor: 'text-stone-400' },
  warning: { bg: 'bg-amber-50', subColor: 'text-amber-500' },
  alert: { bg: 'bg-rose-50', subColor: 'text-rose-500' },
  success: { bg: 'bg-sage-50', subColor: 'text-sage-500' },
}

export default function MetricCard({ emoji, label, value, sub, variant = 'default' }: Props) {
  const { bg, subColor } = variantStyles[variant]
  return (
    <div className={`${bg} rounded-2xl border border-stone-100 p-4 flex flex-col gap-1`}>
      <span className="text-3xl leading-none">{emoji}</span>
      <span className="text-xs uppercase tracking-widest text-stone-400 mt-1">{label}</span>
      <span className="font-serif text-4xl leading-none text-stone-900">{value}</span>
      <span className={`text-sm font-medium ${subColor}`}>{sub}</span>
    </div>
  )
}
