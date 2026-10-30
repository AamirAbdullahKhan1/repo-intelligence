import { Link } from 'react-router-dom'
import {
  Shield,
  Network,
  GitBranch,
  ShieldAlert,
  FileText,
  Package,
  ArrowRight,
  Sparkles,
} from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { RepoInputPanel } from '../components/RepoInputPanel'
import { BackendStatusCard } from '../components/BackendStatusCard'
import { EmptyState } from '../components/EmptyState'
import { RepositorySummaryCard } from '../components/RepositorySummaryCard'
import { useAnalysis } from '../context/AnalysisContext'

const MILESTONE_FEATURES = [
  {
    icon: ShieldAlert,
    title: 'Threat Model Engine',
    description: 'Evidence-linked security findings with SDLC recommendations.',
    milestone: 'Milestone 4',
  },
  {
    icon: FileText,
    title: 'PDF Security Report',
    description: 'Professionally formatted, exportable security assessment.',
    milestone: 'Milestone 5',
  },
]

export function Dashboard() {
  const {
    inventory,
    architecture,
    isAnalyzing,
    error,
    analyzeGithub,
    analyzeZip,
  } = useAnalysis()

  return (
    <div className="px-6 py-6 max-w-5xl mx-auto space-y-6">
      <PageHeader
        title="Repo Intelligence"
        description="AI-assisted repository analysis for architecture understanding and security assessment."
        badge={
          <span className="badge badge-green">Milestone 3 — Architecture & Workflows</span>
        }
      />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Repository Input */}
        <RepoInputPanel
          isAnalyzing={isAnalyzing}
          onAnalyzeGithub={analyzeGithub}
          onAnalyzeZip={analyzeZip}
          errorMessage={error}
        />

        {/* Backend Status & Capabilities */}
        <div className="space-y-4">
          <BackendStatusCard />

          <div className="card">
            <h2 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-brand-400" aria-hidden="true" />
              Repository Analysis Capabilities
            </h2>
            <ul className="space-y-2 text-xs text-gray-400 leading-relaxed">
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                <span>
                  <strong className="text-gray-300">Live GitHub & ZIP Ingestion:</strong> Safe shallow clone with hook suppression & Zip-Slip protection.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                <span>
                  <strong className="text-gray-300">Deterministic Code Inventory:</strong> Languages, manifests, routes, databases, and auth mechanisms.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                <span>
                  <strong className="text-gray-300">Interactive Architecture Diagram:</strong> React Flow component graph with trust boundaries.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                <span>
                  <strong className="text-gray-300">Workflow Execution Paths:</strong> End-to-end request, auth, and CI/CD lifecycle step mappings.
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Ready Navigation Pill when analyzed */}
      {inventory && architecture && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-brand-950/40 border border-brand-500/30 text-xs">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <p className="font-semibold text-gray-100">
                Architecture & Workflows Ready for {inventory.repo_name}
              </p>
              <p className="text-gray-400 mt-0.5">
                {architecture.nodes.length} component nodes, {architecture.edges.length} relationships, and {architecture.workflows.length} workflows extracted.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link
              to="/architecture"
              className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5"
            >
              <Network className="w-3.5 h-3.5" />
              View Architecture
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link
              to="/workflows"
              className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
            >
              <GitBranch className="w-3.5 h-3.5" />
              Explore Workflows
            </Link>
          </div>
        </div>
      )}

      {/* Repository Summary */}
      {inventory ? (
        <RepositorySummaryCard inventory={inventory} />
      ) : (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-200">
              Repository Summary
            </h2>
            <span className="badge badge-gray">No repository analysed</span>
          </div>
          <EmptyState
            icon={Package}
            title="No repository loaded"
            description="Enter a public GitHub repository URL or upload a ZIP archive above to reconstruct its architecture and workflows."
          />
        </div>
      )}

      {/* Upcoming Features */}
      <div>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Upcoming Milestones
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {MILESTONE_FEATURES.map(({ icon: Icon, title, description, milestone }) => (
            <div
              key={title}
              className="bg-surface-800 border border-surface-600 rounded-xl p-4 opacity-75 hover:opacity-100 transition-opacity"
              aria-label={`${title} — planned for ${milestone}`}
            >
              <div className="w-8 h-8 rounded-lg bg-surface-700 flex items-center justify-center mb-3">
                <Icon className="w-4 h-4 text-brand-400" aria-hidden="true" />
              </div>
              <p className="text-xs font-medium text-gray-300 mb-1">{title}</p>
              <p className="text-xs text-gray-500 leading-relaxed">{description}</p>
              <span className="mt-2 badge badge-blue inline-block">{milestone}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
