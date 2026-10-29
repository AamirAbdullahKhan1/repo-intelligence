interface PageHeaderProps {
  title: string
  description: string
  badge?: React.ReactNode
}

export function PageHeader({ title, description, badge }: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-xl font-semibold text-gray-100">{title}</h1>
          {badge}
        </div>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
    </div>
  )
}
