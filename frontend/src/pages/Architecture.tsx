import { Network } from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'

export function Architecture() {
  return (
    <div className="px-6 py-6 max-w-5xl mx-auto">
      <PageHeader
        title="Architecture"
        description="Interactive component diagram — extracted from static code analysis."
        badge={<span className="badge badge-gray">Planned · Milestone 3</span>}
      />
      <div className="card min-h-96">
        <EmptyState
          icon={Network}
          title="No architecture data"
          description="Analyse a repository first. The architecture map will display identified components, services, and data-flow edges."
          badge="Requires Milestone 2 analysis engine"
        />
      </div>
    </div>
  )
}
