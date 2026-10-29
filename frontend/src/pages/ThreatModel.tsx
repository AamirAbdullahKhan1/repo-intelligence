import { ShieldAlert } from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'

export function ThreatModel() {
  return (
    <div className="px-6 py-6 max-w-5xl mx-auto">
      <PageHeader
        title="Threat Model"
        description="Evidence-linked security findings and SDLC recommendations."
        badge={<span className="badge badge-gray">Planned · Milestone 4</span>}
      />
      <div className="card min-h-96">
        <EmptyState
          icon={ShieldAlert}
          title="No threat model"
          description="Security findings will distinguish verified code evidence, reasonable inferences, and unknowns. No findings are fabricated."
          badge="Requires Milestone 3 architecture model"
        />
      </div>
    </div>
  )
}
