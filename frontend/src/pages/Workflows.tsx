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
          title="Workflow Sequence & Job Analysis"
          description="Milestone 2 route and manifest analysis is complete. In Milestone 3, sequential request flows and message queue workflows will be visually mapped."
          badge="Queued for Milestone 3"
        />
      </div>
    </div>
  )
}
