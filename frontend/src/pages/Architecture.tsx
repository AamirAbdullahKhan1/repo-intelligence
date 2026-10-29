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
          title="Interactive Architecture Map"
          description="Milestone 2 code inventory is complete. In Milestone 3, React Flow will render identified microservices, routers, data pipelines, and external integrations."
          badge="Queued for Milestone 3"
        />
      </div>
    </div>
  )
}
