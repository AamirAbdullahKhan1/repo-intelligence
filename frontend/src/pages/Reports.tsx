import { FileText } from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'

export function Reports() {
  return (
    <div className="px-6 py-6 max-w-5xl mx-auto">
      <PageHeader
        title="Reports"
        description="Export a professionally formatted PDF security assessment report."
        badge={<span className="badge badge-gray">Planned · Milestone 5</span>}
      />
      <div className="card min-h-96">
        <EmptyState
          icon={FileText}
          title="No reports generated"
          description="PDF reports will be available once a threat model has been produced. Reports include evidence citations and source references."
          badge="Requires Milestone 4 threat model"
        />
      </div>
    </div>
  )
}
