import { useEffect, useState } from "react";
import type { Entity, EntityPage } from "../../../../shared/contracts/analysis";
import { api } from "../../services/analysis";
export function HierarchyExplorer({
  snapshot,
  path,
  onBrowse,
  onFunction,
  onInspect,
  onError,
}: {
  snapshot: string;
  path: Entity[];
  onBrowse: (n: Entity) => void;
  onFunction: (n: Entity) => void;
  onInspect: (id: string) => void;
  onError: (s: string) => void;
}) {
  const [query, setQuery] = useState(""),
    [offset, setOffset] = useState(0),
    [page, setPage] = useState<EntityPage | null>(null);
  const parent = path[path.length - 1]?.id || "";
  useEffect(() => {
    setQuery("");
    setOffset(0);
  }, [snapshot, parent]);
  useEffect(() => {
    let active = true;
    setPage(null);
    const timer = setTimeout(
      () =>
        api
          .hierarchy(snapshot, parent, query, offset)
          .then((v) => {
            if (active) setPage(v);
          })
          .catch((e) => {
            if (active) onError(e.message);
          }),
      180,
    );
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [snapshot, parent, query, offset]);
  return (
    <aside className="hierarchy-explorer" aria-label="Repository explorer">
      <h3>
        {!parent
          ? "Applications & packages"
          : path[path.length - 1]?.kind === "component"
            ? "Functions & classes"
            : "Logical modules"}
      </h3>
      <p>Source ownership, not a deployment map.</p>
      <input
        aria-label="Search current level"
        placeholder="Search this level…"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOffset(0);
        }}
      />
      {!page ? (
        <p>Loading level…</p>
      ) : (
        <>
          <small>
            {page.total} items · showing {page.total ? offset + 1 : 0}–
            {Math.min(offset + 30, page.total)}
          </small>
          <div className="hierarchy-items">
            {page.items.map((n) => (
              <button
                key={n.id}
                data-entity-id={n.id}
                onClick={() =>
                  n.can_expand
                    ? onBrowse(n)
                    : ["symbol", "endpoint"].includes(n.kind)
                      ? onFunction(n)
                      : onInspect(n.id)
                }
              >
                <span className="hierarchy-kind">
                  {n.kind === "application"
                    ? "package"
                    : n.kind === "component"
                      ? "module"
                      : n.kind === "symbol"
                        ? n.declaration_kind?.includes("Class")
                          ? "class"
                          : n.declaration_kind?.includes("Interface")
                            ? "interface"
                            : "function / method"
                        : n.kind.replaceAll("_", " ")}
                </span>
                <strong>{n.label}</strong>
                <small>{n.group || n.file || n.technology || n.role}</small>
                {n.stats && (
                  <small>
                    {n.stats.components
                      ? `${n.stats.components} modules · `
                      : ""}
                    {n.stats.symbols} code declarations · {n.stats.entry_points}{" "}
                    routes
                  </small>
                )}
                {Boolean(n.stats?.unresolved) && (
                  <span className="unresolved-count">
                    {n.stats?.unresolved} references need context
                  </span>
                )}
              </button>
            ))}
          </div>
          <div className="pager">
            <button
              disabled={!offset}
              onClick={() => setOffset(Math.max(0, offset - 30))}
            >
              Previous
            </button>
            <button
              disabled={offset + 30 >= page.total}
              onClick={() => setOffset(offset + 30)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </aside>
  );
}
