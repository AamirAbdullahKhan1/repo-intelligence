// Public contract. Backend JSON schemas live in shared/schemas; IDs are snapshot-scoped.
export interface Entity {
  id: string;
  kind: string;
  label: string;
  evidence_ids: string[];
  file?: string;
  application_id?: string;
  technology?: string;
  boundary?: string;
  method?: string;
  path?: string;
  profile?: string;
  component_id?: string;
  group?: string;
  canonical_id?: string;
  role?: string;
  can_expand?: boolean;
  resolution?: string;
  reason?: string;
  declaration_kind?: string;
  stats?: Record<string, number>;
  members?: string[];
}
export interface Edge {
  id: string;
  source: string;
  target: string;
  kind: string;
  evidence_ids: string[];
  resolution?: string;
  derivation?: string;
  count?: number;
  limitation?: string;
  support_edge_ids?: string[];
}
export interface Evidence {
  id: string;
  file: string;
  start: number;
  end: number;
  line: number;
  column: number;
  end_line?: number;
  sha256: string;
  rule: string;
  origin?: string;
}
export interface EvidenceResponse {
  snapshot_id: string;
  record: Record<string, unknown>;
  evidence: Evidence[];
  truncated: boolean;
}
export interface Job {
  id: string;
  status: "queued" | "running" | "complete" | "failed" | "cancelled";
  phase: string;
  progress: number;
  created_at: string;
  snapshot_id: string | null;
  error: string | null;
}
export interface Analysis {
  snapshot_id: string;
  repository: string;
  created_at: string;
  provenance: Record<string, string>;
  coverage: Record<string, unknown>;
  counts: Record<string, number>;
  unknown_counts: Record<string, number>;
  scope: Record<string, unknown>;
  tools: Record<string, unknown>;
  inventory: Record<string, unknown>;
  diagnostics: Record<string, unknown>[];
}
export type ViewKind = "system" | "workflow";
export interface View {
  snapshot_id: string;
  kind: ViewKind;
  nodes: Entity[];
  edges: Edge[];
  metadata: Record<string, unknown>;
}
export interface Unknowns {
  total: number;
  items: {
    id: string;
    kind: string;
    file: string;
    line?: number;
    reason: string;
    resolution: string;
    source_id?: string;
    evidence_ids?: string[];
  }[];
}

export interface EntityPage {
  snapshot_id: string;
  parent_id?: string | null;
  total: number;
  offset: number;
  limit: number;
  items: Entity[];
}
export interface RepositoryOverview {
  snapshot_id: string;
  languages: Record<string, number>;
  frameworks: string[];
  packages: Entity[];
  package_count: number;
  packages_truncated: boolean;
  integration_count: number;
  storage_count: number;
  module_count: number;
  entry_point_count: number;
  integrations: Entity[];
  storage: Entity[];
  infrastructure_count: number;
  supported_relationships: number;
  unresolved_references: number;
  relationship_statuses: Record<string, number>;
  coverage: {
    inventoried_files: number;
    parsed_files: number;
    syntax_failures: number;
    skipped_files: number;
  };
  limitations: string[];
}
export interface ToolState {
  version?: string | null;
  loaded_version?: string;
  installed: boolean;
  integration_status: string;
  required: boolean;
  used_by?: string;
  status: string;
  module_path?: string;
  metadata_matches_loaded?: boolean;
}
export interface ToolReport {
  interpreter: string;
  prefix: string;
  base_prefix: string;
  meaning: string;
  syft_role: string;
  tools: Record<string, ToolState>;
}
