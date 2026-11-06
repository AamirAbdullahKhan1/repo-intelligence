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
import {
  toolStatusLabels,
  overviewPresentation,
} from "../services/presentation";

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
    [section, setSection] = useState("overview"),
    [layer, setLayer] = useState("source");
  const [path, setPath] = useState<Entity[]>([]),
    [entry, setEntry] = useState(""),
    [entryQuery, setEntryQuery] = useState(""),
    [entryOffset, setEntryOffset] = useState(0),
    [candidates, setCandidates] = useState<EntityPage | null>(null);
  const [components, setComponents] = useState<Entity[]>([]);
  const [connections, setConnections] = useState(false);
  const [depth, setDepth] = useState(2),
    [limit, setLimit] = useState(18),
    [nested, setNested] = useState(false),
    [dependencies, setDependencies] = useState(false),
    [showUnknown, setShowUnknown] = useState(false);
  const [view, setView] = useState<View | null>(null),
    [record, setRecord] = useState("");
  const [viewError, setViewError] = useState("");
  const scope = path.length ? path[path.length - 1].id : "";
  useEffect(() => {
    let active = true;
    setOverview(null);
    setPath([]);
    setEntry("");
    setRecord("");
    setKind("system");
    setSection("overview");
    setLayer("source");
    setLimit(18);
    setDependencies(false);
    setNested(false);
    setShowUnknown(false);
    setComponents([]);
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
    setViewError("");
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
          section === "overview" ? 40 : limit,
          nested,
          scope,
          showUnknown,
          connections,
        )
        .then((v) => {
          if (active) setView(v);
        })
        .catch((e) => {
          if (active) {
            setViewError(e.message);
            onError(e.message);
          }
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
    section,
  ]);
  function selectSection(next: string) {
    setSection(next);
    setRecord("");
    setKind(next === "workflow" ? "workflow" : "system");
    setLayer(next === "deployment" ? "infrastructure" : "source");
    if (next === "overview" || next === "deployment") {
      setPath([]);
      setEntry("");
      setDependencies(false);
      setConnections(false);
    }
    setLimit(next === "overview" ? 18 : 24);
  }
  useEffect(() => {
    let active = true;
    if (selected && overview)
      api
        .view(
          selected,
          "system",
          "",
          2,
          false,
          "source",
          40,
          false,
          "",
          false,
          false,
        )
        .then((v) => {
          if (active)
            setComponents(v.nodes.filter((n) => n.kind === "component"));
        })
        .catch((e) => {
          if (active) onError(e.message);
        });
    return () => {
      active = false;
    };
  }, [selected, overview]);
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
    setSection(
      section === "code" || n.kind !== "component" ? "code" : "workflow",
    );
  }
  function chooseFunction(n: Entity) {
    setEntry(n.id);
    setKind("workflow");
    setRecord("");
    setSection(section === "code" ? "code" : "workflow");
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
  const displayedView =
    view && section === "overview" ? overviewPresentation(view) : view;
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
              <p>
                Understand the main parts first. Explore their code and evidence
                when needed.
              </p>
            </div>
            <span className="status-pill">
              Static analysis · AI-independent
            </span>
          </header>
          {summary.coverage.standard_library_files === undefined && (
            <p className="view-note legacy-notice">
              Older scan: this result predates the compiler-library fix. Run a
              new scan to apply current analysis; you can delete outdated
              results from Saved analyses.
            </p>
          )}
          {overview && (
            <>
              <p className="analysis-stack">
                {Object.keys(overview.languages)
                  .filter((n) => !n.includes("inventory"))
                  .join(" · ")}{" "}
                <span>{overview.frameworks.join(" · ")}</span>
              </p>
              <details className="repository-context">
                <summary>Repository summary & analysis coverage</summary>
                <RepositoryOverview value={overview} />
              </details>
            </>
          )}
          <nav className="result-sections" aria-label="Analysis views">
            {[
              ["overview", "Architecture overview"],
              ["workflow", "Workflows"],
              ["code", "Code explorer"],
              ["deployment", "Declared deployment"],
              ["uncertainty", "Needs context"],
              ["diagnostics", "Diagnostics"],
            ].map(([id, label]) => (
              <button
                key={id}
                aria-current={section === id ? "page" : undefined}
                className={section === id ? "active" : ""}
                onClick={() => selectSection(id)}
              >
                {label}
              </button>
            ))}
          </nav>
          {(section === "workflow" || section === "code") && (
            <nav className="breadcrumbs" aria-label="Architecture hierarchy">
              <button
                onClick={() => {
                  setPath([]);
                  setEntry("");
                  setRecord("");
                  setKind(section === "workflow" ? "workflow" : "system");
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
                      setKind(
                        section === "workflow" || n.kind === "component"
                          ? "workflow"
                          : "system",
                      );
                    }}
                  >
                    {n.label}
                  </button>
                </span>
              ))}
            </nav>
          )}
          {["overview", "workflow", "code", "deployment"].includes(section) && (
            <>
              <div className="diagram-introduction">
                <div>
                  <span className="eyebrow">
                    {section === "overview"
                      ? "THE BIG PICTURE"
                      : section === "workflow"
                        ? "FOLLOW THE CONNECTIONS"
                        : section === "deployment"
                          ? "CONFIGURATION EVIDENCE"
                          : "EXPLORE THE SOURCE"}
                  </span>
                  <h3>
                    {section === "overview"
                      ? "Overall architecture"
                      : section === "workflow"
                        ? "Inside a component"
                        : section === "deployment"
                          ? "Declared deployment"
                          : "Code explorer"}
                  </h3>
                  <p>
                    {section === "overview"
                      ? "Major responsibilities and the connections supported by this analysis. Select a box or arrow to inspect its evidence."
                      : section === "workflow"
                        ? "Choose a component and an entry point. Arrows show static relationships, not a guaranteed execution sequence."
                        : section === "deployment"
                          ? "Resources and placement declared in configuration. This does not verify what is currently deployed."
                          : "Browse packages, source modules, functions and classes."}
                  </p>
                </div>
                {section === "overview" && (
                  <button
                    className="explore-primary"
                    onClick={() => selectSection("workflow")}
                  >
                    Explore a component →
                  </button>
                )}
              </div>
              {section === "workflow" && (
                <div className="component-picker">
                  <label>
                    Component{" "}
                    <select
                      aria-label="Workflow component"
                      value={scope}
                      onChange={(e) => {
                        const n = components.find(
                          (n) => n.id === e.target.value,
                        );
                        if (n) browse(n);
                        else {
                          setPath([]);
                          setEntry("");
                        }
                      }}
                    >
                      <option value="">All components</option>
                      {scope && !components.some((n) => n.id === scope) && (
                        <option value={scope}>{selectionName}</option>
                      )}
                      {components.map((n) => (
                        <option key={n.id} value={n.id}>
                          {n.label}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              )}
              {(section === "workflow" || section === "code") && (
                <details
                  className="view-options"
                  open={section === "workflow" ? true : undefined}
                >
                  <summary>
                    {section === "workflow"
                      ? "Entry point & exploration controls"
                      : "Exploration controls"}
                  </summary>
                  <div className="view-toolbar">
                    {section === "code" && (
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
                    )}
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
                              Suggested:{" "}
                              {candidates?.items.find(
                                (n) => n.id === view?.metadata.entry_id,
                              )?.label || "entry for this selection"}
                            </option>
                            {entry &&
                              !candidates?.items.some(
                                (n) => n.id === entry,
                              ) && (
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
                              !candidates ||
                              entryOffset + 30 >= candidates.total
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
                      <details className="advanced-controls">
                        <summary>Advanced options</summary>
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
                                onChange={(e) =>
                                  setShowUnknown(e.target.checked)
                                }
                              />{" "}
                              Unresolved markers
                            </label>
                          </>
                        )}
                      </details>
                    </div>
                  </div>
                </details>
              )}
              <p className="view-note">
                {section === "overview"
                  ? view?.metadata.abstraction === "entry-point capabilities"
                    ? "Capabilities follow public routes and supported implementation paths. Helpers may be shared; these are not separate deployed services."
                    : "Derived responsibility groups are logical views, not separate deployed services. Unclassified code remains available in Code explorer."
                  : section === "deployment"
                    ? "Configuration declarations are separate from source operations."
                    : `Exploring ${selectionName}. Select a relationship for supporting evidence.`}{" "}
                {Boolean(view?.metadata.truncated) && (
                  <strong>
                    Some groups or destinations are omitted. Explore a component
                    or open Code explorer for detail.
                  </strong>
                )}
                {section === "overview" &&
                  Number(displayedView?.metadata.overview_hidden_nodes || 0) >
                    0 && (
                    <span>
                      {" "}
                      Helper groups and additional relationships are available
                      in Code explorer.
                    </span>
                  )}
              </p>
              {section === "overview" &&
                view &&
                ![
                  "technical responsibilities",
                  "entry-point capabilities",
                ].includes(String(view.metadata.abstraction)) && (
                  <p className="view-note legacy-notice">
                    This saved analysis uses the older source grouping. Run a
                    new scan to generate responsibility-based architecture; the
                    historical result is preserved.
                  </p>
                )}
              <div
                className={`exploration-workspace ${section !== "code" ? "diagram-first" : ""} ${record ? "with-inspector" : ""}`}
              >
                {section === "code" && (
                  <HierarchyExplorer
                    snapshot={selected}
                    path={path}
                    onBrowse={browse}
                    onFunction={chooseFunction}
                    onInspect={setRecord}
                    onError={onError}
                  />
                )}
                <section
                  className="diagram"
                  aria-label={
                    section === "overview"
                      ? "Overall architecture diagram"
                      : section === "deployment"
                        ? "Declared deployment diagram"
                        : kind === "system"
                          ? "Code architecture diagram"
                          : "Core workflow diagram"
                  }
                >
                  {view ? (
                    <ArchitectureCanvas
                      view={displayedView || view}
                      onSelect={setRecord}
                      panelOpen={Boolean(record)}
                    />
                  ) : (
                    <div
                      className="canvas-message"
                      role={viewError ? "alert" : "status"}
                    >
                      {viewError || "Loading this view…"}
                    </div>
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
                {section === "code" && (
                  <span>
                    Blue dashed: imports · Purple dotted: declarations · Faint
                    dashed: ownership
                  </span>
                )}
              </div>
              {section === "overview" &&
                view?.nodes.some((n) => n.kind === "external_service") && (
                  <details className="http-destinations">
                    <summary>
                      HTTP destinations referenced by source (
                      {
                        view.nodes.filter((n) => n.kind === "external_service")
                          .length
                      }
                      )
                    </summary>
                    <p>
                      These hosts are listed separately to keep the overview
                      readable. Select one for its evidence.
                    </p>
                    <div>
                      {view.nodes
                        .filter((n) => n.kind === "external_service")
                        .map((n) => (
                          <button key={n.id} onClick={() => setRecord(n.id)}>
                            {n.label}
                          </button>
                        ))}
                    </div>
                  </details>
                )}
              <p className="confidence-note">
                Only supported static relationships are shown. Missing arrows do
                not prove isolation. Select an item for evidence; runtime
                execution remains unverified.
              </p>
              {section === "overview" &&
                overview &&
                overview.storage_count > 0 &&
                !view?.nodes.some((n) => n.kind === "storage") && (
                  <p className="confidence-note">
                    Storage declarations are available in Declared deployment;
                    source-to-resource links remain incomplete in this overview.
                  </p>
                )}
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
