import { GitBranch } from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'

export function Workflows() {
  return (
    <div className="px-6 py-6 max-w-5xl mx-auto">
      <PageHeader
        title="Workflows"
        description="Identified request flows, background jobs, and service integrations."
        badge={<span className="badge badge-gray">Planned · Milestone 3</span>}
      />
      <div className="card min-h-96">
        <EmptyState
          icon={GitBranch}
          title="No workflow data"
          description="Workflows are extracted from route analysis, background task patterns, and integration points detected in the repository."
          badge="Requires Milestone 2 analysis engine"
        />
      </div>
    </div>
  )
}
