const CLASSES: Record<string, string> = {
  LOW: 'bg-risk-low-bg text-green-700 ring-1 ring-green-200',
  MODERATE: 'bg-risk-moderate-bg text-yellow-700 ring-1 ring-yellow-200',
  HIGH: 'bg-risk-high-bg text-orange-700 ring-1 ring-orange-200',
  CRITICAL: 'bg-risk-critical-bg text-red-700 ring-1 ring-red-200',
}

export default function RiskBadge({ level }: { level: string }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
        CLASSES[level] ?? 'bg-slate-100 text-slate-600 ring-1 ring-slate-200'
      }`}
    >
      {level}
    </span>
  )
}
