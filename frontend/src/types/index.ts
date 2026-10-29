// ── API Response Types ────────────────────────────────────────────────────────

export interface HealthResponse {
  service: string
  status: 'ok'
  version: string
  environment: string
}

export interface Capability {
  id: string
  name: string
  description: string
  status: 'implemented' | 'planned'
}

export interface CapabilitiesResponse {
  service: string
  capabilities: Capability[]
}

export interface ApiError {
  error: string
  detail: string
}

// ── Repository Inventory Types (Milestone 2) ───────────────────────────────────

export interface LanguageStat {
  name: string
  files_count: number
  bytes_count: number
  percentage: number
}

export interface Dependency {
  name: string
  version?: string | null
  source_file: string
  is_dev: boolean
}

export interface RouteFinding {
  method: string
  path: string
  file: string
  line_number?: number | null
}

export interface ComponentFinding {
  category: 'framework' | 'database' | 'authentication' | 'infrastructure' | string
  name: string
  evidence_type: 'verified_code_evidence' | 'reasonable_inference' | 'unknown'
  file_references: string[]
  details?: string | null
}

export interface RepositoryInventory {
  repo_name: string
  source_type: 'github' | 'zip'
  languages: LanguageStat[]
  primary_language?: string | null
  frameworks: string[]
  manifests: string[]
  dependencies: Dependency[]
  entry_points: string[]
  routes: RouteFinding[]
  databases: ComponentFinding[]
  authentication: ComponentFinding[]
  infrastructure: ComponentFinding[]
  total_files: number
  total_bytes: number
  summary: string
}

export interface AnalysisResponse {
  status: 'success'
  inventory: RepositoryInventory
}

// ── Application State Types ───────────────────────────────────────────────────

export type BackendStatus = 'checking' | 'connected' | 'error'

export type InputMode = 'github' | 'zip'

export interface AnalysisState {
  status: 'idle' | 'loading' | 'success' | 'error'
  message?: string
}

export interface NavItem {
  label: string
  path: string
  icon: string
  disabled?: boolean
}
