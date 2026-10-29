import { useState } from 'react'
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
import { RepositorySummaryCard } from '../components/RepositorySummaryCard'
import { api, ApiClientError } from '../services/api'
import type { RepositoryInventory } from '../types'

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
  const [inventory, setInventory] = useState<RepositoryInventory | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  async function handleAnalyzeGithub(url: string) {
    setIsAnalyzing(true)
    setErrorMessage(null)
    try {
      const res = await api.analyzeGithub(url)
      setInventory(res.inventory)
    } catch (err) {
      if (err instanceof ApiClientError) {
        setErrorMessage(err.message)
      } else {
        setErrorMessage('Failed to analyze repository. Check your connection to the server.')
      }
    } finally {
      setIsAnalyzing(false)
    }
  }

  async function handleAnalyzeZip(file: File) {
    setIsAnalyzing(true)
    setErrorMessage(null)
    try {
      const res = await api.analyzeZip(file)
      setInventory(res.inventory)
    } catch (err) {
      if (err instanceof ApiClientError) {
        setErrorMessage(err.message)
      } else {
        setErrorMessage('Failed to analyze uploaded archive. Check your connection to the server.')
      }
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="px-6 py-6 max-w-5xl mx-auto space-y-6">
      <PageHeader
        title="Repo Intelligence"
        description="AI-assisted repository analysis for architecture understanding and security assessment."
        badge={
          <span className="badge badge-green">Milestone 2 — Ingestion & Inventory</span>
        }
      />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Repository Input */}
        <RepoInputPanel
          isAnalyzing={isAnalyzing}
          onAnalyzeGithub={handleAnalyzeGithub}
          onAnalyzeZip={handleAnalyzeZip}
          errorMessage={errorMessage}
        />

        {/* Backend Status & Info */}
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
                  <strong className="text-gray-300">Safe Ingestion:</strong> Shallow git cloning with hook suppression & Zip-Slip protected extraction.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                <span>
                  <strong className="text-gray-300">Code Inventory:</strong> Deterministic language metrics, manifests, and declared dependencies.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                <span>
                  <strong className="text-gray-300">Route & Framework Detection:</strong> Regex/AST detection of HTTP routes and web frameworks.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                <span>
                  <strong className="text-gray-300">Security Indicators:</strong> Database drivers, ORMs, JWT/auth patterns, and container configs.
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>

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
            description="Provide a GitHub URL or upload a ZIP archive above to run deterministic code inventory."
          />
        </div>
      )}

      {/* Upcoming Features */}
      <div>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Upcoming Milestones
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
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
