import type { BackendStatus } from '../types'

interface StatusBadgeProps {
  status: BackendStatus
  showLabel?: boolean
}

export function StatusBadge({ status, showLabel = true }: StatusBadgeProps) {
  const config = {
    checking: { cls: 'badge-gray', label: 'Checking' },
    connected: { cls: 'badge-green', label: 'Connected' },
    error: { cls: 'badge-red', label: 'Offline' },
  }[status]

  return (
    <span className={config.cls}>
      <span
        className={`w-1.5 h-1.5 rounded-full mr-1.5 inline-block ${
          status === 'connected'
            ? 'bg-emerald-400'
            : status === 'error'
              ? 'bg-red-400'
              : 'bg-gray-400'
        }`}
      />
      {showLabel && config.label}
    </span>
  )
}
