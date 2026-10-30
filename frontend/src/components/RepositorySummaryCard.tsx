import { useState } from 'react'
import {
  Package,
  Layers,
  Database,
  Lock,
  Server,
  FileCode,
  FileText,
  CheckCircle2,
  AlertTriangle,
  FolderTree,
  Terminal,
} from 'lucide-react'
import type { RepositoryInventory } from '../types'

interface RepositorySummaryCardProps {
  inventory: RepositoryInventory
}

const METHOD_COLORS: Record<string, string> = {
  GET: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  POST: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
  PUT: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  PATCH: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
  DELETE: 'bg-red-500/15 text-red-400 border-red-500/30',
}

const LANGUAGE_COLORS: Record<string, string> = {
  Python: 'bg-blue-500',
  TypeScript: 'bg-sky-400',
  JavaScript: 'bg-yellow-400',
  Go: 'bg-cyan-400',
  Java: 'bg-orange-500',
  Rust: 'bg-amber-600',
  Dockerfile: 'bg-teal-400',
  YAML: 'bg-indigo-400',
}

export function RepositorySummaryCard({ inventory }: RepositorySummaryCardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'routes' | 'security' | 'deps'>('overview')

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KiB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MiB`
  }

  return (
    <div className="card space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-surface-600">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-100">{inventory.repo_name}</h2>
            <span className="badge badge-blue uppercase text-[10px]">
              {inventory.source_type}
            </span>
            {inventory.primary_language && (
              <span className="badge badge-green text-xs">
                {inventory.primary_language}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-400 mt-1">{inventory.summary}</p>
        </div>

        <div className="flex items-center gap-4 text-xs text-gray-400 flex-shrink-0">
          <div className="text-right">
            <span className="text-gray-500 block">Total Files</span>
            <span className="font-medium text-gray-200">{inventory.total_files}</span>
          </div>
          <div className="w-px h-8 bg-surface-600" />
          <div className="text-right">
            <span className="text-gray-500 block">Code Size</span>
            <span className="font-medium text-gray-200">{formatBytes(inventory.total_bytes)}</span>
          </div>
        </div>
      </div>

      {/* Honest Evidence Pill */}
      <div className="flex items-start gap-2.5 p-3 rounded-lg bg-surface-700/60 border border-surface-500 text-xs text-gray-300">
        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-gray-200">Verified Code Evidence:</span>{' '}
          All findings below are extracted directly from manifests, file definitions, and static AST/regex patterns.
          Runtime execution paths and reachability are not claimed.
        </div>
      </div>

      {/* Tabs */}
      <div className="flex rounded-lg bg-surface-700 p-1 w-fit" role="tablist">
        <button
          type="button"
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
            activeTab === 'overview'
              ? 'bg-surface-500 text-gray-100 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Overview & Languages
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('routes')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
            activeTab === 'routes'
              ? 'bg-surface-500 text-gray-100 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Terminal className="w-3.5 h-3.5" />
          Routes ({inventory.routes.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('security')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
            activeTab === 'security'
              ? 'bg-surface-500 text-gray-100 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Lock className="w-3.5 h-3.5" />
          Security & Database ({inventory.databases.length + inventory.authentication.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('deps')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
            activeTab === 'deps'
              ? 'bg-surface-500 text-gray-100 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Package className="w-3.5 h-3.5" />
          Manifests & Dependencies ({inventory.dependencies.length})
        </button>
      </div>

      {/* TAB 1: OVERVIEW & LANGUAGES */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Language Breakdown */}
          <div>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
              Language Breakdown
            </h3>
            {/* Visual Bar */}
            <div className="w-full h-3 rounded-full overflow-hidden flex bg-surface-700 mb-3">
              {inventory.languages.map((lang) => (
                <div
                  key={lang.name}
                  style={{ width: `${lang.percentage}%` }}
                  className={`h-full ${LANGUAGE_COLORS[lang.name] || 'bg-brand-500'}`}
                  title={`${lang.name}: ${lang.percentage}%`}
                />
              ))}
            </div>

            <div className="flex flex-wrap gap-3">
              {inventory.languages.map((lang) => (
                <div
                  key={lang.name}
                  className="flex items-center gap-2 text-xs bg-surface-700/50 px-2.5 py-1.5 rounded-md border border-surface-600"
                >
                  <span
                    className={`w-2 h-2 rounded-full ${
                      LANGUAGE_COLORS[lang.name] || 'bg-brand-500'
                    }`}
                  />
                  <span className="font-medium text-gray-200">{lang.name}</span>
                  <span className="text-gray-400">{lang.percentage}%</span>
                  <span className="text-gray-500">({lang.files_count} files)</span>
                </div>
              ))}
            </div>
          </div>

          {/* Frameworks & Entry Points */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-surface-700/30 border border-surface-600">
              <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-2 mb-3">
                <Layers className="w-4 h-4 text-brand-400" />
                Detected Frameworks
              </h3>
              {inventory.frameworks.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {inventory.frameworks.map((fw) => (
                    <span key={fw} className="badge badge-blue text-xs py-1 px-2.5">
                      {fw}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-500">No major standard web framework detected.</p>
              )}
            </div>

            <div className="p-4 rounded-lg bg-surface-700/30 border border-surface-600">
              <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-2 mb-3">
                <FolderTree className="w-4 h-4 text-brand-400" />
                Application Entry Points
              </h3>
              {inventory.entry_points.length > 0 ? (
                <ul className="space-y-1.5 text-xs text-gray-300">
                  {inventory.entry_points.map((ep) => (
                    <li key={ep} className="flex items-center gap-2 font-mono text-[11px] text-brand-300">
                      <FileCode className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                      {ep}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-gray-500">No standard entry points found.</p>
              )}
            </div>
          </div>

          {/* Infrastructure */}
          {inventory.infrastructure.length > 0 && (
            <div className="p-4 rounded-lg bg-surface-700/30 border border-surface-600">
              <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-2 mb-3">
                <Server className="w-4 h-4 text-brand-400" />
                Infrastructure & Deployment
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {inventory.infrastructure.map((inf) => (
                  <div key={inf.name} className="p-2.5 rounded bg-surface-700/50 border border-surface-600 text-xs">
                    <span className="font-medium text-gray-200 block">{inf.name}</span>
                    <span className="text-gray-400 text-[11px]">{inf.details}</span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {inf.file_references.map((f) => (
                        <span key={f} className="font-mono text-[10px] text-gray-400 bg-surface-800 px-1 rounded">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: ROUTES */}
      {activeTab === 'routes' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Discovered HTTP Endpoints ({inventory.routes.length})
            </h3>
            <span className="text-[11px] text-gray-500">Identified via AST and decorator patterns</span>
          </div>

          {inventory.routes.length > 0 ? (
            <div className="border border-surface-600 rounded-lg overflow-hidden max-h-96 overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-700/80 text-gray-400 sticky top-0 border-b border-surface-600">
                  <tr>
                    <th className="py-2 px-3 font-medium">Method</th>
                    <th className="py-2 px-3 font-medium">Route Path</th>
                    <th className="py-2 px-3 font-medium">Declared File</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-600/50 text-gray-300 font-mono text-[11px]">
                  {inventory.routes.map((r, idx) => (
                    <tr key={`${r.method}-${r.path}-${idx}`} className="hover:bg-surface-700/40">
                      <td className="py-2 px-3">
                        <span className={`badge text-[10px] py-0 px-2 font-bold ${METHOD_COLORS[r.method] || 'badge-gray'}`}>
                          {r.method}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-brand-200 font-semibold">{r.path}</td>
                      <td className="py-2 px-3 text-gray-400">
                        {r.file}{r.line_number ? `:${r.line_number}` : ''}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-xs text-gray-500 p-4 border border-surface-600 rounded-lg">
              No declared HTTP routes were found in the analyzed source code.
            </p>
          )}
        </div>
      )}

      {/* TAB 3: SECURITY & DATABASE */}
      {activeTab === 'security' && (
        <div className="space-y-5">
          {/* Databases */}
          <div>
            <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-emerald-400" />
              Database Access & Storage ({inventory.databases.length})
            </h3>
            {inventory.databases.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {inventory.databases.map((db) => (
                  <div key={db.name} className="p-3 rounded-lg bg-surface-700/40 border border-surface-600 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-gray-200">{db.name}</span>
                      <span className="badge badge-green text-[10px]">{db.evidence_type}</span>
                    </div>
                    <p className="text-gray-400 text-[11px] mb-2">{db.details}</p>
                    {db.file_references.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {db.file_references.map((f) => (
                          <span key={f} className="font-mono text-[10px] text-gray-400 bg-surface-800 px-1.5 py-0.5 rounded">
                            {f}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 p-3 bg-surface-700/20 border border-surface-600 rounded-lg">
                No database drivers or connection patterns detected.
              </p>
            )}
          </div>

          {/* Authentication */}
          <div>
            <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-2 mb-3">
              <Lock className="w-4 h-4 text-amber-400" />
              Authentication & Security Mechanisms ({inventory.authentication.length})
            </h3>
            {inventory.authentication.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {inventory.authentication.map((auth) => (
                  <div key={auth.name} className="p-3 rounded-lg bg-surface-700/40 border border-surface-600 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-gray-200">{auth.name}</span>
                      <span className="badge badge-yellow text-[10px]">{auth.evidence_type}</span>
                    </div>
                    <p className="text-gray-400 text-[11px] mb-2">{auth.details}</p>
                    {auth.file_references.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {auth.file_references.map((f) => (
                          <span key={f} className="font-mono text-[10px] text-gray-400 bg-surface-800 px-1.5 py-0.5 rounded">
                            {f}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 p-3 bg-surface-700/20 border border-surface-600 rounded-lg">
                No standard authentication libraries detected in manifests.
              </p>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: MANIFESTS & DEPENDENCIES */}
      {activeTab === 'deps' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Manifest Files Detected
            </h3>
            <span className="text-[11px] text-gray-500">{inventory.manifests.length} manifest(s)</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {inventory.manifests.map((m) => (
              <span key={m} className="flex items-center gap-1.5 font-mono text-xs text-brand-300 bg-surface-700 px-2.5 py-1 rounded border border-surface-600">
                <FileText className="w-3.5 h-3.5 text-gray-400" />
                {m}
              </span>
            ))}
          </div>

          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider pt-2">
            Extracted Dependencies ({inventory.dependencies.length})
          </h3>

          {inventory.dependencies.length > 0 ? (
            <div className="border border-surface-600 rounded-lg overflow-hidden max-h-72 overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-700/80 text-gray-400 sticky top-0 border-b border-surface-600">
                  <tr>
                    <th className="py-2 px-3 font-medium">Package</th>
                    <th className="py-2 px-3 font-medium">Version Constraint</th>
                    <th className="py-2 px-3 font-medium">Manifest Source</th>
                    <th className="py-2 px-3 font-medium">Type</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-600/50 text-gray-300 font-mono text-[11px]">
                  {inventory.dependencies.map((dep, idx) => (
                    <tr key={`${dep.name}-${idx}`} className="hover:bg-surface-700/40">
                      <td className="py-1.5 px-3 font-semibold text-gray-200">{dep.name}</td>
                      <td className="py-1.5 px-3 text-gray-400">{dep.version || '*'}</td>
                      <td className="py-1.5 px-3 text-gray-500">{dep.source_file}</td>
                      <td className="py-1.5 px-3">
                        {dep.is_dev ? (
                          <span className="badge badge-gray text-[10px]">dev</span>
                        ) : (
                          <span className="badge badge-blue text-[10px]">prod</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-xs text-gray-500">No dependency entries parsed.</p>
          )}
        </div>
      )}
    </div>
  )
}

