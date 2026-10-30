import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Network,
  GitBranch,
  ShieldAlert,
  FileText,
  Shield,
  Wifi,
  WifiOff,
  Loader2,
  FolderGit2,
} from 'lucide-react'
import type { BackendStatus } from '../types'
import { useAnalysis } from '../context/AnalysisContext'

interface SidebarProps {
  backendStatus: BackendStatus
}

const NAV_ITEMS = [
  { label: 'Overview', path: '/overview', icon: LayoutDashboard },
  { label: 'Architecture', path: '/architecture', icon: Network },
  { label: 'Workflows', path: '/workflows', icon: GitBranch },
  { label: 'Threat Model', path: '/threat-model', icon: ShieldAlert },
  { label: 'Reports', path: '/reports', icon: FileText },
]

function BackendStatusIndicator({ status }: { status: BackendStatus }) {
  if (status === 'checking') {
    return (
      <span className="flex items-center gap-1.5 text-xs text-gray-500">
        <Loader2 className="w-3 h-3 animate-spin" />
        Connecting…
      </span>
    )
  }
  if (status === 'connected') {
    return (
      <span className="flex items-center gap-1.5 text-xs text-emerald-400">
        <Wifi className="w-3 h-3" />
        API connected
      </span>
    )
  }
  return (
    <span className="flex items-center gap-1.5 text-xs text-red-400">
      <WifiOff className="w-3 h-3" />
      API offline
    </span>
  )
}

export function Sidebar({ backendStatus }: SidebarProps) {
  const { inventory } = useAnalysis()

  return (
    <aside className="w-60 flex-shrink-0 bg-surface-800 border-r border-surface-600 flex flex-col">
      {/* Brand */}
      <div className="px-4 pt-5 pb-4 border-b border-surface-600">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-100 leading-none">
              Repo Intelligence
            </p>
            <p className="text-xs text-gray-500 mt-0.5">Security Platform</p>
          </div>
        </div>
      </div>

      {/* Active Repository Pill */}
      {inventory && (
        <div className="mx-3 mt-3 p-2.5 rounded-lg bg-surface-700/60 border border-surface-600 text-xs">
          <div className="flex items-center gap-2 text-brand-300 font-medium truncate">
            <FolderGit2 className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="truncate">{inventory.repo_name}</span>
          </div>
          <p className="text-[10px] text-gray-400 mt-0.5">
            {inventory.primary_language || 'Repo'} · {inventory.total_files} files
          </p>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1" aria-label="Main navigation">
        {NAV_ITEMS.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              isActive ? 'nav-item-active' : 'nav-item'
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Backend Status Footer */}
      <div className="px-4 py-3 border-t border-surface-600">
        <BackendStatusIndicator status={backendStatus} />
        <p className="text-xs text-gray-600 mt-1.5">v0.1.0 · Milestone 3</p>
      </div>
    </aside>
  )
}
