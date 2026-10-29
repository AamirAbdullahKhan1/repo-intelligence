import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  badge?: string
}

export function EmptyState({ icon: Icon, title, description, badge }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
      <div className="w-12 h-12 rounded-xl bg-surface-700 border border-surface-500 flex items-center justify-center mb-4">
        <Icon className="w-6 h-6 text-gray-500" aria-hidden="true" />
      </div>
      <h3 className="text-sm font-medium text-gray-300 mb-1">{title}</h3>
      <p className="text-xs text-gray-500 max-w-xs leading-relaxed">{description}</p>
      {badge && (
        <span className="mt-3 badge badge-gray">{badge}</span>
      )}
    </div>
  )
}
