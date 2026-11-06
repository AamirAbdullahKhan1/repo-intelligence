import { useEffect, useRef, useState } from "react";
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
  const [flow, setFlow] = useState<Awaited<
    ReturnType<typeof api.flowEvidence>
  > | null>(null);
  const [flowBusy, setFlowBusy] = useState(false);
  const flowGeneration = useRef(0);
  useEffect(() => {
    let active = true;
    setResult(null);
    setError("");
    setFlow(null);
    setFlowBusy(false);
    flowGeneration.current++;
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
  const loadFlow = async () => {
    const generation = flowGeneration.current;
    setFlowBusy(true);
    try {
      const next = await api.flowEvidence(
        snapshot,
        record,
        flow?.items.length || 0,
      );
      if (generation !== flowGeneration.current) return;
      setFlow((previous) => ({
        ...next,
        items: [...(previous?.items || []), ...next.items],
      }));
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Could not load value-flow evidence",
      );
    } finally {
      if (generation === flowGeneration.current) setFlowBusy(false);
    }
  };
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
          {(Boolean(item.flow_step_ids) || Boolean(item.support_edge_ids)) && (
            <details>
              <summary>Value-flow derivation</summary>
              {!flow && (
                <button disabled={flowBusy} onClick={loadFlow}>
                  Load value-flow steps
                </button>
              )}
              {flow && (
                <>
                  <p>
                    {flow.note}
                    {flow.partial
                      ? " The flow analysis has reported limits."
                      : ""}
                  </p>
                  {flow.total === 0 && (
                    <p>
                      This relationship has no value-flow derivation; inspect
                      its source relationships.
                    </p>
                  )}
                  {flow.items.map((step) => (
                    <div className="citation" key={step.id}>
                      <small>
                        {step.kind.replaceAll("_", " ").toLowerCase()}
                      </small>
                      {step.locations.map((location, index) => (
                        <div key={index}>
                          <code>
                            {location.file}:{location.line}:{location.column}
                          </code>
                        </div>
                      ))}
                    </div>
                  ))}
                  {flow.items.length < flow.total && (
                    <button disabled={flowBusy} onClick={loadFlow}>
                      More flow steps ({flow.items.length}/{flow.total})
                    </button>
                  )}
                </>
              )}
            </details>
          )}
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
