import type { View } from "../../../shared/contracts/analysis";

// Presentation-only subgraph. Canonical identities and evidence remain unchanged.
export function overviewPresentation(view: View): View {
  if (view.metadata.abstraction !== "technical responsibilities") return view;
  const responsibilities = view.nodes.filter(
    (n) =>
      n.projection_rule === "responsibility-v1" &&
      !["Other analyzed source", "Library integration"].includes(n.group || ""),
  );
  if (!responsibilities.length) return view;
  const groups = new Set(responsibilities.map((n) => n.id));
  const byId = new Map(view.nodes.map((n) => [n.id, n]));
  const links = view.edges.filter(
    (e) =>
      groups.has(e.source) &&
      (groups.has(e.target) ||
        ["sdk", "storage"].includes(byId.get(e.target)?.kind || "")),
  );
  const targets = new Set(links.map((e) => e.target));
  const nodes = [
    ...responsibilities,
    ...view.nodes.filter((n) => targets.has(n.id) && !groups.has(n.id)),
  ].slice(0, 16);
  const visible = new Set(nodes.map((n) => n.id));
  const edges = links.filter(
    (e) => visible.has(e.source) && visible.has(e.target),
  );
  return {
    ...view,
    nodes,
    edges,
    metadata: {
      ...view.metadata,
      focused_overview: true,
      overview_hidden_nodes: view.nodes.length - nodes.length,
      overview_hidden_edges: view.edges.length - edges.length,
    },
  };
}

export const relationLabels: Record<string, string> = {
  CALLS: "Function call",
  MAY_INVOKE_CALLBACK: "Possible callback invocation",
  CONSTRUCTS: "Constructor call",
  HANDLED_BY: "Route handler",
  MODULE_REFERENCE: "Uses module",
  CONTAINS_COMPONENT: "Contains module",
  SDK_USAGE: "SDK library usage",
  USES_SDK: "Uses SDK libraries",
  SDK_API_CALL: "SDK call",
  CONSTRUCTS_CLIENT: "Creates SDK client",
  HTTP_INTEGRATION: "HTTP integration",
  CALLS_HTTP: "HTTP call",
  USES_RESOURCE: "Resource operation",
  RESOURCE_USAGE: "Uses resource",
  HANDLER_REFERENCE: "Handled by",
  IMPORTS: "Import dependency",
  IMPORT_DEPENDENCY: "Import dependency",
  REEXPORTS: "Re-export",
  TYPE_REFERENCES: "Type dependency",
  DEFINED_IN: "Defined in file",
  CONTAINS_SYMBOL: "Nested definition",
  BINDS_RESOURCE: "Resource declaration",
  BINDS_SERVICE: "Service binding declaration",
  DECLARES_CONTAINER: "Container declaration",
  CONFIGURES_LOG_SINK: "Log sink declaration",
  STARTS_AFTER: "Startup dependency declaration",
  ENTRYPOINT_PACKAGE: "Declared entry package",
  UNRESOLVED_REFERENCE: "Unresolved reference",
};
export const statusLabels: Record<string, string> = {
  confirmed: "Source-supported",
  resolved: "Source-supported",
  conditional: "Conditional",
  ambiguous: "Ambiguous",
  unresolved: "Unresolved",
};
export function relationshipLabel(kind: string) {
  return relationLabels[kind] || kind.toLowerCase().replaceAll("_", " ");
}
export const toolStatusLabels: Record<string, string> = {
  active: "Integrated and active",
  installed_unused: "Installed but unused",
  deferred: "Deferred intentionally",
  missing_required: "Missing but required",
  removed: "Removed",
};
