import type {
  Analysis,
  EntityPage,
  RepositoryOverview,
  ToolReport,
  Entity,
  EvidenceResponse,
  Job,
  Unknowns,
  View,
  ViewKind,
} from "../../../shared/contracts/analysis";
const base = "/api/v1";
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(base + url, options);
  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(
      typeof error?.detail === "string"
        ? error.detail
        : `Request failed (${response.status})`,
    );
  }
  return response.json();
}
export const api = {
  overview: (id: string) =>
    request<RepositoryOverview>(`/analyses/${id}/overview`),
  tools: () => request<ToolReport>("/tools"),
  hierarchy: (id: string, parent: string, query: string, offset = 0) =>
    request<EntityPage>(
      `/analyses/${id}/hierarchy?${new URLSearchParams({ ...(parent ? { parent_id: parent } : {}), query, offset: String(offset) })}`,
    ),
  candidates: (id: string, scope: string, query: string, offset = 0) =>
    request<EntityPage>(
      `/analyses/${id}/explore/entries?${new URLSearchParams({ ...(scope ? { scope_id: scope } : {}), query, offset: String(offset) })}`,
    ),
  github: (url: string) =>
    request<Job>("/analyze/github", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    }),
  zip: (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return request<Job>("/analyze/upload", { method: "POST", body });
  },
  job: (id: string) => request<Job>(`/jobs/${id}`),
  cancel: (id: string) =>
    request<Job>(`/jobs/${id}/cancel`, { method: "POST" }),
  history: () => request<Analysis[]>("/analyses"),
  analysis: (id: string) => request<Analysis>(`/analyses/${id}`),
  entries: (id: string) => request<Entity[]>(`/analyses/${id}/entries`),
  view: (
    id: string,
    kind: ViewKind,
    entry: string,
    depth: number,
    dependencies: boolean,
    layer: string,
    limit: number,
    nested: boolean,
    scope: string,
    showUnknown: boolean,
    connections: boolean,
  ) =>
    request<View>(
      `/analyses/${id}/view?${new URLSearchParams({ kind, depth: String(depth), dependencies: String(dependencies), layer, limit: String(limit), nested: String(nested), ...(scope ? { scope_id: scope } : {}), show_unknown: String(showUnknown), connections: String(connections), ...(entry ? { entry_id: entry } : {}) })}`,
    ),
  evidence: (
    id: string,
    record: string,
    kind: ViewKind,
    layer: string,
    scope: string,
    limit: number,
    dependencies: boolean,
  ) =>
    request<EvidenceResponse>(
      `/analyses/${id}/evidence?${new URLSearchParams({ record_id: record, kind, layer, ...(scope ? { scope_id: scope } : {}), view_limit: String(limit), dependencies: String(dependencies) })}`,
    ),
  unknowns: (id: string, offset = 0, scope = "") =>
    request<Unknowns>(
      `/analyses/${id}/unknowns?offset=${offset}&scope_id=${encodeURIComponent(scope)}`,
    ),
};
