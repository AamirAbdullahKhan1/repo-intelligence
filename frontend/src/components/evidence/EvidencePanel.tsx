import { useEffect, useState } from "react";
import type {
  Entity,
  EvidenceResponse,
  ViewKind,
} from "../../../../shared/contracts/analysis";
import { api } from "../../services/analysis";
import { relationshipLabel, statusLabels } from "../../services/presentation";
export function EvidencePanel({
  snapshot,
  record,
  kind,
  layer,
  scope,
  limit,
  dependencies,
  onExplore,
  onBrowse,
  onInspect,
  onClose,
}: {
  snapshot: string;
  record: string;
  kind: ViewKind;
  layer: string;
  scope: string;
  limit: number;
  dependencies: boolean;
  onExplore: (id: string) => void;
  onBrowse: (n: Entity) => void;
  onInspect: (id: string) => void;
  onClose: () => void;
}) {
  const [result, setResult] = useState<EvidenceResponse | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setResult(null);
    setError("");
    api
      .evidence(snapshot, record, kind, layer, scope, limit, dependencies)
      .then((v) => {
        if (active) setResult(v);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [snapshot, record, kind, layer, scope, limit, dependencies]);
  const item = result?.record;
  const status = String(item?.resolution || "confirmed");
  const supporting = (item?.supporting_relationships || []) as {
    id: string;
    kind: string;
    source_label: string;
    target_label: string;
  }[];
  const citation = (e: NonNullable<typeof result>["evidence"][number]) => (
    <div key={e.id} className="citation">
      <code>
        {e.file}:{e.line}:{e.column}
        {e.end_line && e.end_line !== e.line ? `–${e.end_line}` : ""}
      </code>
      <small>
        {e.rule} · {e.origin || "source code"}
      </small>
      <details>
        <summary>Source identity and range</summary>
        <small>
          Evidence {e.id}
          <br />
          SHA-256 {e.sha256}
          <br />
          UTF-16 offsets {e.start}–{e.end}
        </small>
      </details>
    </div>
  );
  return (
    <aside className="evidence-panel" aria-label="Evidence inspector">
      <div className="panel-heading">
        <h3>Evidence inspector</h3>
        <button aria-label="Close inspector" onClick={onClose}>
          ×
        </button>
      </div>
      {error ? (
        <p role="alert">{error}</p>
      ) : !result || !item ? (
        <p>Loading source support…</p>
      ) : (
        <>
          <span className={`status-badge ${status}`}>
            {statusLabels[status] || status}
          </span>
          <h4>{String(item.label || relationshipLabel(String(item.kind)))}</h4>
          <dl className="record-facts">
            <dt>Type</dt>
            <dd>{relationshipLabel(String(item.kind))}</dd>
            {Boolean(item.source) && (
              <>
                <dt>Caller / source</dt>
                <dd>{String(item.source_label || item.source)}</dd>
                <dt>Target</dt>
                <dd>{String(item.target_label || item.target)}</dd>
              </>
            )}
            {Boolean(item.file) && (
              <>
                <dt>Source file</dt>
                <dd>{String(item.file)}</dd>
              </>
            )}
            {Boolean(item.count) && (
              <>
                <dt>Grouped source sites</dt>
                <dd>{String(item.count)}</dd>
              </>
            )}
          </dl>
          <p>
            {String(
              item.derivation ||
                item.reason ||
                item.boundary ||
                item.identity ||
                "A source declaration recorded in the saved graph.",
            )}
          </p>
          <p className="evidence-limit">
            {String(
              item.limitation ||
                "Static support is not a guaranteed runtime execution sequence.",
            )}
          </p>
          {item.kind === "symbol" && (
            <button
              className="explore-button"
              onClick={() => onExplore(String(item.id))}
            >
              Explore calls from this function
            </button>
          )}
          {["application", "component", "architecture_group"].includes(
            String(item.kind),
          ) && (
            <button
              className="explore-button"
              onClick={() => onBrowse(item as unknown as Entity)}
            >
              Open {item.kind === "component" ? "module" : "contents"}
            </button>
          )}
          <h5>Supporting source locations</h5>
          {result.evidence.length ? (
            result.evidence.slice(0, 3).map(citation)
          ) : (
            <p>
              No direct source citation on this boundary. Inspect a supported
              connection or its canonical children.
            </p>
          )}
          {result.evidence.length > 3 && (
            <details>
              <summary>
                More source locations ({result.evidence.length - 3})
              </summary>
              {result.evidence.slice(3).map(citation)}
            </details>
          )}
          {result.truncated && (
            <p>
              First 100 citations shown; original evidence IDs remain on the
              grouped record.
            </p>
          )}
          {!!supporting.length && (
            <details>
              <summary>Inspect individual supporting relationships</summary>
              {supporting.map((e) => (
                <button
                  className="support-record"
                  key={e.id}
                  onClick={() => onInspect(e.id)}
                >
                  {e.source_label} → {e.target_label}
                  <small>{relationshipLabel(e.kind)}</small>
                </button>
              ))}
              <small>
                Showing up to 10 source relationships from the group.
              </small>
            </details>
          )}
          <details>
            <summary>Record identity</summary>
            <code className="identity">{String(item.id)}</code>
            <p>
              {Array.isArray(item.members)
                ? `${item.members.length} original entity IDs in this group.`
                : item.canonical_id
                  ? "Original canonical entity ID retained."
                  : "Source IDs and evidence are retained in the saved graph."}
            </p>
          </details>
        </>
      )}
    </aside>
  );
}
