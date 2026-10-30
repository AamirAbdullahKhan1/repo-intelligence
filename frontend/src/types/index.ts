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

// ── Repository Inventory Types ─────────────────────────────────────────────────

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

// ── Architecture & Workflow Models (V2 Multi-Layer & Hierarchical) ─────────────

export type ArchitectureNodeType =
  | 'client'
  | 'frontend_app'
  | 'api_service'
  | 'mcp_server'
  | 'worker'
  | 'serverless_function'
  | 'database'
  | 'cache'
  | 'auth'
  | 'shared_library'
  | 'infrastructure'
  | 'external_service'

export type ArchitectureEdgeType =
  | 'IMPORTS'
  | 'CALLS'
  | 'HANDLES_ROUTE'
  | 'READS_FROM'
  | 'WRITES_TO'
  | 'CONNECTS_TO'
  | 'PUBLISHES_EVENT'
  | 'CONSUMES_EVENT'
  | 'DEPLOYED_AS'
  | 'TRIGGERS_WORKFLOW'
  | 'DEPENDS_ON'

export type ConfidenceLevel = 'VERIFIED' | 'INFERRED' | 'UNKNOWN'

export interface EvidenceMeta {
  file_path: string
  line_start?: number | null
  line_end?: number | null
  evidence_category: string
  extraction_method: string
  confidence: ConfidenceLevel
  snippet?: string | null
}

export interface ArchitectureNode {
  id: string
  label: string
  type: ArchitectureNodeType
  category: string
  technology?: string | null
  level?: number
  parent_id?: string | null
  file_references: string[]
  confidence: ConfidenceLevel
  description?: string | null
  sub_modules?: string[]
  evidence?: EvidenceMeta | null
  metadata?: Record<string, any>
}

export interface ArchitectureEdge {
  id: string
  source: string
  target: string
  label: string
  relationship_type: ArchitectureEdgeType
  confidence: ConfidenceLevel
  evidence_file?: string | null
  line_number?: number | null
  evidence?: EvidenceMeta | null
  description?: string | null
}

export interface WorkflowStep {
  step_number: number
  component_id: string
  component_label: string
  action: string
  file_reference?: string | null
  line_number?: number | null
  confidence: ConfidenceLevel
}

export interface WorkflowModel {
  id: string
  name: string
  description: string
  trigger: string
  steps: WorkflowStep[]
  components_involved: string[]
}

export interface DeploymentModel {
  nodes: ArchitectureNode[]
  edges: ArchitectureEdge[]
  pipeline_stages: string[]
}

export interface ArchitectureModel {
  repo_name: string
  nodes: ArchitectureNode[]
  edges: ArchitectureEdge[]
  workflows: WorkflowModel[]
  deployment_view: DeploymentModel
  explanation: string
  llm_enhanced: boolean
  model_used?: string | null
}

export interface AnalysisResponse {
  status: 'success'
  inventory: RepositoryInventory
  architecture: ArchitectureModel
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
