import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  GitBranch,
  ArrowRight,
  Search,
  CheckCircle2,
  FileCode,
  Zap,
  Activity,
  Layers,
} from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'
import { useAnalysis } from '../context/AnalysisContext'

export function Workflows() {
  const { architecture } = useAnalysis()
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('')

  if (!architecture || !architecture.workflows || architecture.workflows.length === 0) {
    return (
      <div className="px-6 py-6 max-w-5xl mx-auto space-y-6">
        <PageHeader
          title="Workflow Analysis"
          description="Identified request flows, background jobs, and service integrations."
          badge={<span className="badge badge-blue">Milestone 3</span>}
        />
        <div className="card min-h-96 flex flex-col items-center justify-center">
          <EmptyState
            icon={GitBranch}
            title="No Workflows Discovered"
            description="Analyse a repository on the Overview dashboard to reconstruct request execution flows and CI/CD pipelines."
          />
          <Link to="/overview" className="btn-primary mt-4">
            <Search className="w-4 h-4" />
            Go to Overview & Analyse
          </Link>
        </div>
      </div>
    )
  }

  const activeWorkflow =
    architecture.workflows.find((w) => w.id === selectedWorkflowId) ||
    architecture.workflows[0]

  return (
    <div className="px-6 py-6 max-w-5xl mx-auto space-y-6">
      <PageHeader
        title={`Workflows — ${architecture.repo_name}`}
        description="Sequential request lifecycles, authentication flows, and integration pipelines extracted from code evidence."
        badge={
          <span className="badge badge-green flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            {architecture.workflows.length} Workflows Identified
          </span>
        }
      />

      {/* Workflow Tabs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {architecture.workflows.map((wf) => {
          const isSelected = wf.id === activeWorkflow.id
          return (
            <button
              key={wf.id}
              onClick={() => setSelectedWorkflowId(wf.id)}
              className={`text-left p-4 rounded-xl border transition-all duration-150 ${
                isSelected
                  ? 'bg-brand-950/60 border-brand-500 shadow-md ring-1 ring-brand-500'
                  : 'bg-surface-800 border-surface-600 hover:border-surface-500'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="badge badge-blue text-[10px] uppercase flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  {wf.trigger}
                </span>
                <span className="text-xs text-gray-500">{wf.steps.length} steps</span>
              </div>
              <h3 className="text-sm font-semibold text-gray-100">{wf.name}</h3>
              <p className="text-xs text-gray-400 mt-1 line-clamp-2 leading-relaxed">
                {wf.description}
              </p>
            </button>
          )
        })}
      </div>

      {/* Active Workflow Detail Card */}
      <div className="card space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-surface-600">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-brand-400" />
              <h2 className="text-base font-semibold text-gray-100">
                {activeWorkflow.name}
              </h2>
            </div>
            <p className="text-xs text-gray-400 mt-1">{activeWorkflow.description}</p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="text-gray-500">Components:</span>
            <div className="flex flex-wrap gap-1">
              {activeWorkflow.components_involved.map((comp) => (
                <span
                  key={comp}
                  className="badge bg-surface-700 text-gray-300 border border-surface-500 text-[10px]"
                >
                  {comp}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Step-by-step Flow Pipeline */}
        <div className="space-y-4">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
            <Layers className="w-3.5 h-3.5" />
            Execution Step Sequence
          </h3>

          <div className="relative pl-6 space-y-6 before:absolute before:left-3 before:top-3 before:bottom-3 before:w-0.5 before:bg-surface-600">
            {activeWorkflow.steps.map((step, idx) => (
              <div key={step.step_number} className="relative flex items-start gap-4">
                {/* Step indicator node */}
                <div className="absolute -left-6 top-0 w-6 h-6 rounded-full bg-surface-800 border-2 border-brand-500 flex items-center justify-center text-[10px] font-bold text-brand-300 shadow">
                  {step.step_number}
                </div>

                <div className="flex-1 bg-surface-700/50 border border-surface-600 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="badge badge-blue text-xs font-semibold">
                      {step.component_label}
                    </span>
                    <span
                      className={`badge text-[10px] ${
                        step.confidence === 'VERIFIED'
                          ? 'badge-green'
                          : 'badge-gray'
                      }`}
                    >
                      {step.confidence === 'VERIFIED' ? 'VERIFIED' : 'INFERRED'}
                    </span>
                  </div>

                  <p className="text-xs text-gray-200 leading-relaxed font-sans">
                    {step.action}
                  </p>

                  {step.file_reference && (
                    <div className="flex items-center gap-1.5 pt-1 text-xs text-gray-400 font-mono text-[11px]">
                      <FileCode className="w-3.5 h-3.5 text-gray-500" />
                      <span>{step.file_reference}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Evidence Notice */}
        <div className="p-3 rounded-lg bg-surface-700/30 border border-surface-600 text-xs text-gray-400">
          <strong>Notice:</strong> Workflow step ordering combines declared route entry points, middleware interceptors, and database client calls. While component interactions are grounded in static declarations, dynamic branch conditions and runtime failure paths require execution tracing.
        </div>
      </div>
    </div>
  )
}
