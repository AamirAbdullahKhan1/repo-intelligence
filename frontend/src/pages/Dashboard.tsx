import {
  Shield,
  Network,
  GitBranch,
  ShieldAlert,
  FileText,
  Package,
} from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { RepoInputPanel } from '../components/RepoInputPanel'
import { BackendStatusCard } from '../components/BackendStatusCard'
import { EmptyState } from '../components/EmptyState'

const MILESTONE_FEATURES = [
  {
    icon: Network,
    title: 'Architecture Map',
    description: 'Interactive diagram of components, services, and data flows.',
    milestone: 'Milestone 3',
  },
  {
    icon: GitBranch,
    title: 'Workflow Analysis',
    description: 'Identified request paths, background jobs, and integrations.',
    milestone: 'Milestone 3',
  },
  {
    icon: ShieldAlert,
    title: 'Threat Model',
    description: 'Evidence-linked security findings with SDLC recommendations.',
    milestone: 'Milestone 4',
  },
  {
    icon: FileText,
    title: 'PDF Report',
    description: 'Professionally formatted, exportable security assessment.',
    milestone: 'Milestone 5',
  },
]

export function Dashboard() {
  return (
    <div className="px-6 py-6 max-w-5xl mx-auto">
      <PageHeader
        title="Repo Intelligence"
        description="AI-assisted repository analysis for architecture understanding and security assessment."
        badge={
          <span className="badge badge-blue">Milestone 1 — Foundation</span>
        }
      />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        {/* Repository Input */}
        <RepoInputPanel />

        {/* Backend Status */}
        <div className="space-y-4">
          <BackendStatusCard />

          {/* What This Tool Does */}
          <div className="card">
            <h2 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-brand-400" aria-hidden="true" />
              What Repo Intelligence Does
            </h2>
            <ul className="space-y-2 text-xs text-gray-400 leading-relaxed">
              <li className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">·</span>
                Inventories languages, frameworks, routes, and dependencies.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">·</span>
                Reconstructs architecture from static code analysis.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">·</span>
                Uses Azure OpenAI to explain extracted evidence — not to hallucinate structure.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">·</span>
                Generates evidence-linked threat findings distinguishing confirmed evidence,
                inferences, and unknowns.
              </li>
              <li className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">·</span>
                Exports a professional PDF security report.
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Repository Summary — Empty State */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-200">
            Repository Summary
          </h2>
          <span className="badge badge-gray">No repository analysed</span>
        </div>
        <EmptyState
          icon={Package}
          title="No repository loaded"
          description="Provide a GitHub URL or upload a ZIP archive above to begin analysis."
        />
      </div>

      {/* Upcoming Features */}
      <div>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Upcoming Features
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {MILESTONE_FEATURES.map(({ icon: Icon, title, description, milestone }) => (
            <div
              key={title}
              className="bg-surface-800 border border-surface-600 rounded-xl p-4 opacity-60"
              aria-label={`${title} — planned for ${milestone}`}
            >
              <div className="w-8 h-8 rounded-lg bg-surface-700 flex items-center justify-center mb-3">
                <Icon className="w-4 h-4 text-gray-500" aria-hidden="true" />
              </div>
              <p className="text-xs font-medium text-gray-300 mb-1">{title}</p>
              <p className="text-xs text-gray-500 leading-relaxed">{description}</p>
              <span className="mt-2 badge badge-gray inline-block">{milestone}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
