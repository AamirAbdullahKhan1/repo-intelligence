import { useEffect, useState } from "react";
import type { Unknowns } from "../../../../shared/contracts/analysis";
import { api } from "../../services/analysis";
export function UncertaintyPanel({
  snapshot,
  scope,
  onSelect,
  onError,
}: {
  snapshot: string;
  scope: string;
  onSelect: (id: string) => void;
  onError: (s: string) => void;
}) {
  const [page, setPage] = useState<Unknowns | null>(null),
    [offset, setOffset] = useState(0);
  useEffect(() => {
    setOffset(0);
  }, [scope, snapshot]);
  useEffect(() => {
    let active = true;
    setPage(null);
    api
      .unknowns(snapshot, offset, scope)
      .then((v) => {
        if (active) setPage(v);
      })
      .catch((e) => {
        if (active) onError(e.message);
      });
    return () => {
      active = false;
    };
  }, [snapshot, scope, offset]);
  return (
    <section className="uncertainty-panel" aria-label="Unresolved references">
      <h3>
        References needing context {page && `· ${page.total.toLocaleString()}`}
      </h3>
      <p>
        These records do not establish a target or communication path. The list
        follows the selected package/module.
      </p>
      {!page ? (
        <p>Loading references…</p>
      ) : (
        <>
          {page.items.map((u) => (
            <button
              key={u.id}
              className="issue-row"
              onClick={() => onSelect(u.id)}
            >
              <span className="status-badge unresolved">
                Unresolved {u.kind}
              </span>
              <code>
                {u.file}:{u.line || 1}
              </code>
              <span>{u.reason}</span>
              <small>Inspect source support →</small>
            </button>
          ))}
          {!page.items.length && (
            <p>
              No unresolved references recorded for this selection. This does
              not prove analysis completeness.
            </p>
          )}
          <div className="pager">
            <button
              disabled={!offset}
              onClick={() => setOffset(Math.max(0, offset - 30))}
            >
              Previous
            </button>
            <span>
              {page.total ? offset + 1 : 0}–{Math.min(offset + 30, page.total)}{" "}
              of {page.total}
            </span>
            <button
              disabled={offset + 30 >= page.total}
              onClick={() => setOffset(offset + 30)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </section>
  );
}
