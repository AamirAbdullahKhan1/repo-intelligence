import { useEffect, useState } from "react";
import type {
  Analysis,
  Entity,
  EntityPage,
  RepositoryOverview as Overview,
  ToolReport,
  View,
  ViewKind,
} from "../../../shared/contracts/analysis";
import { api } from "../services/analysis";
import { ArchitectureCanvas } from "../components/diagrams/ArchitectureCanvas";
import { EvidencePanel } from "../components/evidence/EvidencePanel";
import { UncertaintyPanel } from "../components/evidence/UncertaintyPanel";
import { RepositoryOverview } from "../components/repository/RepositoryOverview";
import { HierarchyExplorer } from "../components/repository/HierarchyExplorer";
import { toolStatusLabels } from "../services/presentation";

export function Architecture({
  selected,
  summary,
  error,
  onDismiss,
  onError,
}: {
  selected: string;
  summary: Analysis | null;
  error: string;
  onDismiss: () => void;
  onError: (s: string) => void;
}) {
  const [overview, setOverview] = useState<Overview | null>(null),
    [tools, setTools] = useState<ToolReport | null>(null);
  const [kind, setKind] = useState<ViewKind>("system"),
    [section, setSection] = useState("architecture"),
    [layer, setLayer] = useState("source");
  const [path, setPath] = useState<Entity[]>([]),
    [entry, setEntry] = useState(""),
    [entryQuery, setEntryQuery] = useState(""),
    [entryOffset, setEntryOffset] = useState(0),
    [candidates, setCandidates] = useState<EntityPage | null>(null);
  const [connections, setConnections] = useState(false);
  const [depth, setDepth] = useState(2),
    [limit, setLimit] = useState(24),
    [nested, setNested] = useState(false),
    [dependencies, setDependencies] = useState(false),
    [showUnknown, setShowUnknown] = useState(false);
  const [view, setView] = useState<View | null>(null),
    [record, setRecord] = useState("");
  const scope = path.length ? path[path.length - 1].id : "";
  useEffect(() => {
    let active = true;
    setOverview(null);
    setPath([]);
    setEntry("");
    setRecord("");
    setKind("system");
    setSection("architecture");
    setLayer("source");
    setEntryQuery("");
    setEntryOffset(0);
    if (selected)
      api
        .overview(selected)
        .then((v) => {
          if (active) setOverview(v);
        })
        .catch((e) => {
          if (active) onError(e.message);
        });
    return () => {
      active = false;
    };
  }, [selected]);
  useEffect(() => {
    let active = true;
    api
      .tools()
      .then((v) => {
        if (active) setTools(v);
      })
      .catch((e) => {
        if (active) onError(e.message);
      });
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    setEntryQuery("");
    setEntryOffset(0);
    setCandidates(null);
  }, [scope, selected]);
  useEffect(() => {
    let active = true;
    if (kind !== "workflow" || !selected) return;
    const timer = setTimeout(
      () =>
        api
          .candidates(selected, scope, entryQuery, entryOffset)
          .then((v) => {
            if (active) setCandidates(v);
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
  }, [selected, scope, entryQuery, entryOffset, kind]);
  useEffect(() => {
    let active = true;
    setView(null);
    setRecord("");
    if (summary && overview)
      api
        .view(
          summary.snapshot_id,
          kind,
          entry,
          depth,
          dependencies,
          layer,
          limit,
          nested,
          scope,
          showUnknown,
          connections,
        )
        .then((v) => {
          if (active) setView(v);
        })
        .catch((e) => {
          if (active) onError(e.message);
        });
    return () => {
      active = false;
    };
  }, [
    summary,
    overview,
    kind,
    entry,
    depth,
    dependencies,
    layer,
    limit,
    nested,
    scope,
    showUnknown,
    connections,
  ]);
  function browse(n: Entity) {
    const owner =
      overview?.packages.find((p) => p.id === n.application_id) ||
      path.find((p) => p.id === n.application_id);
    setPath(
      n.kind === "application" || n.kind === "architecture_group"
        ? [n]
        : owner
          ? [owner, n]
          : [n],
    );
    setEntry("");
    setRecord("");
    setLayer("source");
    setKind(n.kind === "component" ? "workflow" : "system");
    setSection("architecture");
  }
  function chooseFunction(n: Entity) {
    setEntry(n.id);
    setKind("workflow");
    setRecord("");
    setSection("architecture");
  }
  async function explore(id: string) {
    try {
      const response = await api.evidence(
        selected,
        id,
        kind,
        layer,
        scope,
        limit,
        dependencies,
      );
      const n = response.record as unknown as Entity;
      if (n.kind === "symbol" || n.kind === "endpoint") {
        if (n.component_id && n.component_id !== scope) {
          const parent = await api.evidence(
            selected,
            n.component_id,
            kind,
            layer,
            scope,
            limit,
            dependencies,
          );
          browse(parent.record as unknown as Entity);
        }
        chooseFunction(n);
      } else browse(n);
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    }
  }
  const selectionName = path.length
    ? path[path.length - 1].label
    : "Repository";
  return (
    <main className="architecture-page">
      {error && (
        <div role="alert" className="error-banner">
          {error}
          <button onClick={onDismiss}>Dismiss</button>
        </div>
      )}
      {!summary ? (
        <div className="welcome">
          <span className="eyebrow">REPOSITORY ARCHITECTURE</span>
          <h2>Start with the big picture.</h2>
          <p>
            Analyze a public repository or ZIP. Explore its packages, logical
            modules and source-supported relationships without loading every
            function onto one diagram.
          </p>
          <div className="welcome-grid">
            <div>
              <strong>01 · Understand</strong>
              <p>Major modules, declared resources and integrations.</p>
            </div>
            <div>
              <strong>02 · Explore</strong>
              <p>Repository → packages → modules → functions and classes.</p>
            </div>
            <div>
              <strong>03 · Verify</strong>
              <p>Inspect source support and references needing more context.</p>
            </div>
          </div>
        </div>
      ) : (
        <>
          <header className="analysis-header">
            <div>
              <span className="eyebrow">
                SAVED ANALYSIS · {summary.snapshot_id.slice(0, 12)}
              </span>
              <h2>{summary.repository}</h2>
              <p>Explore what the source supports, one level at a time.</p>
            </div>
            <span className="status-pill">
              Static analysis · AI-independent
            </span>
          </header>
          {overview && <RepositoryOverview value={overview} />}
          <nav className="result-sections" aria-label="Analysis sections">
            <button
              className={section === "architecture" ? "active" : ""}
              onClick={() => setSection("architecture")}
            >
              Architecture explorer
            </button>
            <button
              className={section === "uncertainty" ? "active" : ""}
              onClick={() => {
                setSection("uncertainty");
                setRecord("");
              }}
            >
              Needs context{" "}
              {overview && (
                <span>{overview.unresolved_references.toLocaleString()}</span>
              )}
            </button>
            <button
              className={section === "diagnostics" ? "active" : ""}
              onClick={() => {
                setSection("diagnostics");
                setRecord("");
              }}
            >
              Detailed diagnostics & tools
            </button>
          </nav>
          <nav className="breadcrumbs" aria-label="Architecture hierarchy">
            <button
              onClick={() => {
                setPath([]);
                setEntry("");
                setRecord("");
                setKind("system");
              }}
            >
              Repository
            </button>
            {path.map((n, i) => (
              <span key={n.id}>
                {" "}
                /{" "}
                <button
                  onClick={() => {
                    setPath(path.slice(0, i + 1));
                    setEntry("");
                    setRecord("");
                    setKind(n.kind === "component" ? "workflow" : "system");
                  }}
                >
                  {n.label}
                </button>
              </span>
            ))}
          </nav>
          {section === "architecture" && (
            <>
              <div className="view-toolbar">
                <div className="tabs">
                  <button
                    className={kind === "system" ? "active" : ""}
                    onClick={() => {
                      setKind("system");
                      setRecord("");
                    }}
                  >
                    System architecture
                  </button>
                  <button
                    className={kind === "workflow" ? "active" : ""}
                    onClick={() => {
                      setKind("workflow");
                      setRecord("");
                    }}
                  >
                    Core workflow
                  </button>
                </div>
                <div className="workflow-controls">
                  {kind === "system" && (
                    <label>
                      <input
                        type="checkbox"
                        checked={connections}
                        onChange={(e) => {
                          setConnections(e.target.checked);
                          setRecord("");
                        }}
                      />{" "}
                      More module connections
                    </label>
                  )}
                  {kind === "system" ? (
                    <label>
                      Layer{" "}
                      <select
                        aria-label="Architecture layer"
                        value={layer}
                        onChange={(e) => {
                          setLayer(e.target.value);
                          if (e.target.value !== "source") {
                            setPath([]);
                            setEntry("");
                          }
                          setRecord("");
                        }}
                      >
                        <option value="source">
                          Major modules & integrations
                        </option>
                        <option value="infrastructure">
                          Infrastructure declarations
                        </option>
                        <option value="all">Source & infrastructure</option>
                      </select>
                    </label>
                  ) : (
                    <>
                      <input
                        aria-label="Find workflow entry"
                        placeholder="Find a route or function…"
                        value={entryQuery}
                        onChange={(e) => {
                          setEntryQuery(e.target.value);
                          setEntryOffset(0);
                        }}
                      />
                      <select
                        aria-label="Workflow entry"
                        value={entry}
                        onChange={(e) => {
                          setEntry(e.target.value);
                          setRecord("");
                        }}
                      >
                        <option value="">
                          Suggested entry for this selection
                        </option>
                        {entry &&
                          !candidates?.items.some((n) => n.id === entry) && (
                            <option value={entry}>Selected function</option>
                          )}
                        {candidates?.items.map((n) => (
                          <option key={n.id} value={n.id}>
                            {n.label} · {n.file}
                          </option>
                        ))}
                      </select>
                      <button
                        disabled={!entryOffset}
                        onClick={() =>
                          setEntryOffset(Math.max(0, entryOffset - 30))
                        }
                      >
                        Previous entries
                      </button>
                      <button
                        disabled={
                          !candidates || entryOffset + 30 >= candidates.total
                        }
                        onClick={() => setEntryOffset(entryOffset + 30)}
                      >
                        More entries
                      </button>
                      <label>
                        Depth{" "}
                        <select
                          aria-label="Workflow depth"
                          value={depth}
                          onChange={(e) => setDepth(Number(e.target.value))}
                        >
                          {[1, 2, 3, 4, 5, 6].map((n) => (
                            <option key={n}>{n}</option>
                          ))}
                        </select>
                      </label>
                    </>
                  )}
                  <label>
                    Node limit{" "}
                    <select
                      aria-label="Node budget"
                      value={limit}
                      onChange={(e) => {
                        setLimit(Number(e.target.value));
                        setRecord("");
                      }}
                    >
                      {[14, 24, 40, 80].map((n) => (
                        <option key={n}>{n}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={dependencies}
                      onChange={(e) => {
                        setDependencies(e.target.checked);
                        setRecord("");
                      }}
                    />{" "}
                    Import dependencies
                  </label>
                  {kind === "workflow" && (
                    <>
                      <label>
                        <input
                          type="checkbox"
                          checked={nested}
                          onChange={(e) => setNested(e.target.checked)}
                        />{" "}
                        Nested definitions
                      </label>
                      <label>
                        <input
                          type="checkbox"
                          checked={showUnknown}
                          onChange={(e) => setShowUnknown(e.target.checked)}
                        />{" "}
                        Unresolved markers
                      </label>
                    </>
                  )}
                </div>
              </div>
              <p className="view-note">
                {kind === "system"
                  ? "A compact selection of logical source modules. Browse all modules in the explorer. Packages and directories do not imply deployed services."
                  : `Calls within and from ${selectionName}. Choose a source entry or function; arrows do not establish runtime order.`}{" "}
                {Boolean(view?.metadata.truncated) && (
                  <strong>
                    Showing a bounded selection. Browse another module or adjust
                    the limits.
                  </strong>
                )}
              </p>
              <div
                className={`exploration-workspace ${record ? "with-inspector" : ""}`}
              >
                <HierarchyExplorer
                  snapshot={selected}
                  path={path}
                  onBrowse={browse}
                  onFunction={chooseFunction}
                  onInspect={setRecord}
                  onError={onError}
                />
                <section
                  className="diagram"
                  aria-label={
                    kind === "system"
                      ? "System architecture diagram"
                      : "Core workflow diagram"
                  }
                >
                  {view ? (
                    <ArchitectureCanvas
                      view={view}
                      onSelect={setRecord}
                      panelOpen={Boolean(record)}
                    />
                  ) : (
                    <div className="canvas-message">Loading this level…</div>
                  )}
                </section>
                {record && (
                  <EvidencePanel
                    snapshot={selected}
                    record={record}
                    kind={kind}
                    layer={layer}
                    scope={scope}
                    limit={limit}
                    dependencies={dependencies}
                    onExplore={explore}
                    onBrowse={browse}
                    onInspect={setRecord}
                    onClose={() => setRecord("")}
                  />
                )}
              </div>
              <div className="legend">
                <span className="legend-confirmed">● Source-supported</span>
                <span className="legend-conditional">━ Conditional</span>
                <span className="legend-ambiguous">┄ Ambiguous</span>
                <span className="legend-unresolved">┄ Unresolved target</span>
                <span>
                  Blue dashed: imports · Purple dotted: declarations · Faint
                  dashed: ownership
                </span>
              </div>
              <p className="confidence-note">
                A source-supported call identifies a static implementation.
                Runtime conditions and reachability may still be unknown. Groups
                retain original entity, relationship and evidence IDs.
              </p>
            </>
          )}
          {section === "uncertainty" && (
            <div className="uncertainty-workspace">
              <UncertaintyPanel
                snapshot={selected}
                scope={scope}
                onSelect={setRecord}
                onError={onError}
              />
              {record && (
                <EvidencePanel
                  snapshot={selected}
                  record={record}
                  kind={kind}
                  layer={layer}
                  scope={scope}
                  limit={limit}
                  dependencies={dependencies}
                  onExplore={explore}
                  onBrowse={browse}
                  onInspect={setRecord}
                  onClose={() => setRecord("")}
                />
              )}
            </div>
          )}
          {section === "diagnostics" && (
            <section className="diagnostics expanded">
              <h3>Analysis details</h3>
              <p>
                The saved graph is reopened as recorded; viewing it does not
                rerun analysis. Current runtime tools below may differ from
                those used for an older snapshot.
              </p>
              <details>
                <summary>Compiler counters, inventory and scope</summary>
                <pre>
                  {JSON.stringify(
                    {
                      coverage: summary.coverage,
                      inventory: summary.inventory,
                      diagnostics: summary.diagnostics,
                      snapshot_tools: summary.tools,
                      scope: summary.scope,
                    },
                    null,
                    2,
                  )}
                </pre>
              </details>
              <h3>Current backend environment</h3>
              {tools ? (
                <>
                  <p>
                    Interpreter: <code>{tools.interpreter}</code>
                  </p>
                  <p>{tools.meaning}</p>
                  <table className="tool-matrix">
                    <thead>
                      <tr>
                        <th>Tool</th>
                        <th>Version</th>
                        <th>Installed</th>
                        <th>Integration</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(tools.tools).map(([name, t]) => (
                        <tr key={name}>
                          <td>{name}</td>
                          <td>{t.version || "—"}</td>
                          <td>{t.installed ? "Yes" : "No"}</td>
                          <td>
                            {toolStatusLabels[t.integration_status] ||
                              t.integration_status}
                            <small>{t.status}</small>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p>{tools.syft_role}</p>
                  <p>
                    PyYAML loaded version: {tools.tools.pyyaml.loaded_version}.
                    Installed metadata matches loaded module:{" "}
                    {String(tools.tools.pyyaml.metadata_matches_loaded)}.
                  </p>
                </>
              ) : (
                <p>Loading runtime inventory…</p>
              )}
            </section>
          )}
        </>
      )}
    </main>
  );
}
