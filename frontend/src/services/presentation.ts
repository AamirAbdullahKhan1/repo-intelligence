export const relationLabels: Record<string, string> = {
  CALLS: "Function call",
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
