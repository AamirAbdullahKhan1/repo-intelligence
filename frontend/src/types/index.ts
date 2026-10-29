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
