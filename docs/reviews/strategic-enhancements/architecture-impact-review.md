# Architecture impact review

Review date: 31 October 2026. Scope: architectural evaluation only. No application changes, package installation, candidate-tool execution, contract changes or repository rescans were performed for this review.

## Decision

Prioritize correctness, bounded value propagation, and evidence-backed architecture interpretation using the existing compiler. Most proposed tools produce useful inputs or alternative presentations, but do not solve the missing step from source relationships to application responsibilities. Do not add a default chain of scanners.

Adopt an interpretation stage as an internal module, not a new service or independent source of truth. Keep the TypeScript worker, Python coordinator, canonical graph, saved-analysis workflow, React Flow and ELK. Introduce external providers only after a specific gap, safety profile and measurable benefit justify them.

## Evidence and verification boundaries

**Verified now:** current source files, function implementations, tests and dependency manifests were inspected; `app.tooling.inspect()` was run with the backend virtual environment. Official tool documentation and selected upstream source were consulted. This is not a complete source-security audit of any candidate tool.

**Existing recorded evidence:** `output/usability/acceptance.json`, the prior 61-test result, and `output/review/explanation-analysis-probes.json`. Tests and synthetic probes were not rerun for this review. The probe artifact records three earlier synthetic cases, without target execution.

**Not verified:** candidate versions, installation viability on this host, safe invocation profiles, end-to-end sandbox containment, speed/memory improvements, architectural precision, or head-to-head superiority. No candidate was installed or tested. Qualitative cost estimates below are engineering estimates, not benchmarks. Upstream links describe mutable documentation; a future pilot must pin releases and audit that release's implementation.

## Current implementation baseline

Paths below are relative to the workspace root `C:/Users/Asus/OneDrive/Desktop/repo-intelligence`.

| Area | Verified implementation | Status and limits |
|---|---|---|
| Intake | `backend/app/ingestion/github.py:parse_url,retrieve`; `archive.py`; `jobs.py:Jobs` | Implemented: public root GitHub URLs or ZIP; fixed GitHub API/codeload hosts and pinned commit; bounded extraction, no Git invocation, hooks or dependency installs. Private repositories and branch-selection URLs are not supported. |
| Snapshot | `ingestion/snapshot.py`; `analysis/pipeline.py:analyze` | Implemented: read-only flags, byte fingerprints before/after analysis, cleanup. Flags are not an OS sandbox. |
| Coordinator | `analysis/pipeline.py:analyze` | Implemented: fixed trusted Node worker, reduced environment, timeout, output limit, schema validation, configuration augmentation and evidence checking. |
| Source provider | `backend/workers/typescript/index.cjs:walk,resolveOrigin,literal,symbolEntity`; `ts.createProgram`, `getResolvedSignature` | Implemented TS/JS declarations/imports/local-body calls; shallow SDK/value tracking. Not full data-flow, dynamic dispatch or all-language semantics. |
| Frameworks | `workers/typescript/adapters/{next,express,wrangler}.cjs` | Partial: selected route registration and infrastructure patterns. React detection is not full component or execution-context analysis. |
| Configuration | `analysis/configuration.py:augment` | Partial: bounded YAML Compose service and `depends_on` declarations. `STARTS_AFTER` is not communication or runtime readiness. No general Terraform/Kubernetes provider. |
| Evidence | `evidence/validation.py:validate`; `redaction.py` | Implemented identity/range/reference checks and limited redaction. A valid citation does not establish semantic correctness. |
| Canonical graph | `contracts.py:Graph,Entity,Edge,Evidence` | Implemented versioned graph, evidence and unknowns. Extra fields are allowed and relationship kinds are strings; multi-provider semantics are not comprehensively enforced by the schema. |
| Persistence | `persistence/store.py:Store.save,analysis` | Implemented SQLite whole-JSON graph storage; not indexed entity storage or incremental analysis. |
| Interpretation | `index.cjs:component`; `graph/exploration.py:Index.decorate,aggregate` | Partial ownership/role heuristics and aggregation. No dedicated semantic Architecture Interpretation Engine is wired into `analyze`. |
| Projections/API | `graph/projections.py`; `graph/exploration.py:Index`; `api/routes.py:register_routes` | Implemented bounded hierarchy/workflow, summary, evidence and saved analyses. Requests rebuild indexes from stored graphs. |
| Browser | `frontend/src/pages/Architecture.tsx`; `components/diagrams/ArchitectureCanvas.tsx` | Implemented React Flow interaction and layered ELK worker layout. These do not infer responsibilities or missing communication. |
| Evaluation | `backend/tests/test_{application,ingestion,typescript_worker,framework_adapters,exploration,synthetic_monorepo}.py`; browser scripts | Regression/functional checks exist. No labelled architecture corpus, user-comprehension benchmark or measured competitor comparison. |

The production design is a modular monolith with a separate trusted compiler worker. Jobs use two executor threads and a capacity of four active/queued jobs, not a distributed queue.

### Actual dependency state

Fresh backend inspection reported TypeScript 5.9.3, React Flow 11.11.4, ELK.js 0.12.1, SQLite 3.45.3 and PyYAML 6.0.3 active. NetworkX, Syft, Tree-sitter, ast-grep and Semgrep are absent/deferred in the backend report. This report does not inspect every proposed package; unreported candidates must not be called installed or absent based on that report alone.

System-Python NetworkX 3.3 and PyYAML 6.0.2 in `docs/implementation/system-python-tools.json` are historical records for another interpreter. They do not conflict with the active backend environment. No missing required active dependency was reported. Source dependency manifests do not amount to an SBOM.

## Proposal decisions

| Proposal | Recommendation | Expected value | Main benefit | Main drawback | Suggested integration |
|---|---|---|---|---|---|
| A. Syft | Defer | Medium inventory; low immediate architecture | Wider ecosystem package/version evidence | Packages are not services or actual usage; duplicate manifests | Optional package provider after source semantics |
| B. dependency-cruiser | Modify | Medium verification | Compare module edges, cycles and boundary rules | Duplicates imports; configuration/resolution differences | Development comparator, not default provider or truth oracle |
| C. NetworkX/Louvain | Pilot later | Uncertain grouping benefit | Evaluate graph structure as a grouping hint | Structural communities lack architectural meaning | Offline experiment on filtered weighted projection |
| D. Bounded value propagation | Adopt, narrowly | High for selected missing links | Correct reassignment and track config/client origins | Complex joins, aliasing and state explosion | Extend compiler worker, retain unknowns and derivations |
| E. Joern | Pilot later | Potentially high for a chosen new language | Control/data-flow query capabilities | Additional graph/runtime, reconciliation and operational cost | Isolated optional provider experiment, not TS replacement |
| F. Grimp | Modify/defer | Medium Python import coverage | Mature import graph queries | Importability/discovery safety and no call/resource model | Python development comparator after filesystem AST baseline |
| F/I. import-linter | Defer | Medium governance; low reconstruction | Check explicitly supplied layer rules | Rules do not discover architecture; custom code loading | Trusted development contracts only |
| G. LikeC4 | Modify/defer | Medium sharing/export | Architecture model/view export | Second model and rendering stack | One-way optional exporter from canonical projections |
| H. Inframap | Defer | Medium infrastructure-only | Terraform declaration relationships | Provider-specific pruning and application-mapping gap | Optional raw infrastructure input, not final truth |
| I. ast-grep | Pilot only for a gap | Medium syntax-pattern coverage | Rapid rule prototyping across languages | No general cross-file binding; native grammar/config surface | Trusted rule experiments, not second TS engine |
| I. Semgrep CE | Defer | Medium selected patterns; low core gap closure | Local source pattern and limited flow rules | Does not replace cross-file semantic resolution | Optional targeted provider after evidence contract |
| I. Checkov | Defer | Medium future security review | IaC policy findings | Security findings are not architecture edges | Separate diagnostics provider, not architecture inference |
| I. Public typings | Modify/adopt curated pilot | Medium identity/type improvement | Resolve library API signatures more accurately | Declaration is not implementation or observed use | Version-matched, pre-vetted read-only metadata bundle |

“Adopt” is a recommendation, not authorization to implement in this task. Reject default integration of all tools, service discovery by Louvain, treating comparator output as ground truth, and replacing the canonical graph with a vendor graph.

## Individual technical assessments

### A. Syft

Syft distinguishes directory dependency declarations from installed-package evidence and offers selectable catalogers. A source-directory SBOM can improve ecosystem/version visibility without installing target dependencies. It cannot establish a call path or service communication. [Catalogers](https://oss.anchore.com/docs/guides/sbom/catalogers/).

Recommended mapping: manifest/lockfile → declares package; source import → references package; proven receiver/API use → uses integration. Keep package coordinate/version identity separate from remote service identity. A declared Redis package must not become a Redis deployment. Deduplicate package records by ecosystem, normalized coordinate, version and owning manifest/scope; preserve version ranges and unresolved versions. Transitive lockfile dependencies must not all appear in the system view.

A future wrapper should accept only the already extracted directory, use explicit catalogers and trusted config, disable network/update behaviors, and preserve manifest locations. Exact execution/network behavior of a pinned cataloger set remains to be audited. Do not use arbitrary image/registry source detection for this product.

### B. dependency-cruiser

It provides import dependency validation and cycles. Its configuration can be JavaScript; its TS options include path handling and differing treatment of pre-compilation/type dependencies. These differences make it a useful comparator, not an independent accuracy oracle: it may share TypeScript mechanisms and assumptions. [Project](https://github.com/sverweij/dependency-cruiser), [options](https://github.com/sverweij/dependency-cruiser/blob/main/doc/options-reference.md).

Compare equivalent file scopes, module-resolution settings and edge categories on labelled fixtures. Classify disagreements rather than automatically overwriting edges. Never discover or execute client `.dependency-cruiser.*`, Babel/webpack configuration or plugins. Use a fixed programmatic profile or explicit platform-owned configuration only after auditing the pinned version's discovery path. Cycles can initially be calculated using a small SCC algorithm over existing import edges.

### C. NetworkX

Louvain optimizes graph modularity heuristically and uses randomized ordering. Structural groups are not named responsibilities, deployment boundaries or services. [Algorithm documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html).

A pilot should use module-level, typed, weighted source-supported dependencies, excluding ownership/definition edges and isolating type-only edges. Shared utilities can create misleading dense communities. Ambiguous candidate edges should not silently contribute full weight. Unknown targets are not artificial hubs. Fix package/backend/version, seed, insertion order and tie-breaking; a seed alone is insufficient across algorithm versions/backends. Label output as suggested grouping and retain member IDs. Existing standard-library traversal is adequate for current bounded queries; do not install NetworkX merely to replace it.

### D. Bounded reaching definitions/value propagation

This most directly targets current missing/wrong links. First handle reassignment at program points; then immutable imports/exports, finite constant strings, symbolic environment keys, static object properties and small known helper summaries. A reaching definition answers which assignment may supply a value at a particular use. It must not simply take the first initializer or last textual assignment.

Use a finite abstract domain, explicit unknown, bounded alternative sets and deterministic fixed-point processing. Unknown branch conditions retain possible alternatives; any unmodelled write/call invalidates affected conclusions. Loops, mutable closures, object aliases/getters/proxies and dynamic keys may require widening to unknown. Cross-function analysis must model ordering/side effects conservatively. A static singleton does not imply runtime execution.

For endpoint mapping, `/api/x` alone does not prove this repository's server receives it. Determine browser/server context, supported base URL/rewrite configuration, method and route pattern, or retain a candidate. Do not read secret values to resolve symbolic keys. Full JavaScript analysis is out of scope; select useful subsets with negative fixtures.

### E. Joern

Joern exposes CPG data-flow queries and language-specific frontends. Frontend availability is not uniform accuracy. JVM and auxiliary frontend processes add operational overhead; exact release behavior needs investigation. [Data-flow queries](https://docs.joern.io/cpgql/data-flow-steps/), [frontends](https://docs.joern.io/frontends/), [process/memory notes](https://docs.joern.io/installation/).

Do not duplicate the TS worker by default. A research pilot should choose one demanded language such as Java, then compare supported source/call/data-flow facts with a hand-labelled corpus. C/C++ may require unavailable compile configuration; do not generate it by building client code. Use platform-owned query scripts and preinstalled pinned frontends, prohibit downloads/builds, and audit subprocess/filesystem behavior. Import normalized facts and locations, not a second persistent application architecture. Reject findings lacking adequate evidence or mark unsupported locations as diagnostics.

### F. Grimp / import-linter

Grimp exposes Python module imports, import details and graph queries, not function/API/database semantics. Its API expects importable packages; inspected upstream package discovery calls `importlib.util.find_spec`. Python package discovery must not be assumed execution-free for every package shape, parent lookup or import hook. This review did not demonstrate target execution. [Usage](https://grimp.readthedocs.io/en/stable/usage.html), [inspected finder source](https://raw.githubusercontent.com/python-grimp/grimp/main/src/grimp/adaptors/packagefinder.py).

Start Python support with filesystem discovery and the standard `ast` parser. Resolve supported local imports without adding the target to a general import environment. Do not install target packages, process `.pth` files or use target plugins. If Grimp adds sufficient query performance or correctness, pilot controlled discovery in isolation; otherwise retain it only as a comparator. import-linter checks supplied architectural contracts and supports custom contract types; never load client-supplied Python contracts. [Contract types](https://github.com/seddonym/import-linter/blob/main/docs/contract_types/index.md).

### G. LikeC4

LikeC4 models architecture and provides model/diagram exports; it does not discover source relationships. Its CLI also includes Vite-based site building, which is outside repository analysis. [DSL](https://likec4.dev/dsl/intro/), [CLI](https://likec4.dev/tooling/cli/).

Retain React Flow/ELK. First implement direct export of existing projections if sharing is the need. If demand justifies LikeC4 interoperability, generate escaped DSL in a platform-owned output directory, with a canonical-ID/evidence sidecar. Never read target LikeC4/Vite configs or build the submitted project. Treat user-edited exported models as separate documentation, not reverse-imported verified facts. Multi-level diagrams do not justify a competing canonical model.

### H. Inframap

Inframap reads HCL/state and applies resource-specific simplification; its README documents raw output and removal of unconnected nodes by default. Those choices can omit valid declarations, so its simplified graph is unsuitable as our sole evidence source. [README](https://github.com/cycloidio/inframap).

Prefer local HCL declarations as the eventual baseline; require resource-address/source-range mapping. No `terraform init`, plan, apply, backend pull, remote modules, provider execution or Graphviz shell pipelines are needed or authorized. Preserve unresolved module references. Treat state as sensitive and potentially stale, not live cloud proof. Application-resource links need binding/configuration evidence and cannot be inferred because both names contain “database.” Defer until application interpretation is stronger.

### I. Supporting tools

**ast-grep:** useful for syntax recognition, not general symbol/data-flow resolution. Native custom grammar libraries can execute code; use built-in parsers or pre-vetted grammars and platform-owned rules only. Repository config auto-discovery is forbidden. [Custom language mechanism](https://ast-grep.github.io/advanced/custom-language).

**Semgrep CE:** targeted patterns can complement providers, but do not assume cross-file interprocedural capabilities from commercial documentation. Local rules and explicit metrics-off/network denial should be required in a pilot. Never use registry/auto config or authenticated CI integration for client analysis. [CE limitations](https://github.com/semgrep/semgrep/blob/develop/README.md), [metrics behavior](https://github.com/semgrep/semgrep/blob/develop/metrics.md).

**Checkov:** a future security diagnostics input, not an architecture engine. Its CLI supports downloads, external modules/checks and platform access. Disable all such features, do not load repository Python checks, and audit transitive config discovery before use. [CLI controls](https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html).

**Public typings:** declaration metadata describes APIs, not implementations. Maintain curated, version-matched bundles outside uploads, with provenance, licensing and integrity checks. No automatic package install or per-job remote fetch. Reject unknown version matches or label them explicitly. Never convert signature-only calls to local implementation calls. [TypeScript declarations](https://www.typescriptlang.org/tsconfig/declaration.html).

## Execution-safety assessment

All proposed wrappers require read-only snapshot access, isolated output/temp directories, OS-level filesystem/network/process/resource controls and fixed argument arrays. Existing Node API blocking and read-only flags are defense in depth, not OS enforcement. Repository configuration is data only when parsed through an allowlisted non-executing parser. No repository plugins, scripts, native extensions or arbitrary commands are permitted.

The table describes documented surfaces and recommended restrictions, not tested containment. “None required” means the proposed narrow use needs no network or external commands; it is not a claim about every mode of a tool.

| Tool | File-only use possible? / external programs | Repository configuration or extension risk | Network surface | Required gate before pipeline use |
|---|---|---|---|---|
| Syft | Directory cataloging intended; exact catalogers untested | Auto config/env and cataloger behavior need pin/audit | Other source types/update/remote behaviors must be excluded | Explicit local source/catalogers/config, no credentials, deny egress |
| dependency-cruiser | Source parsing intended; external renderer unnecessary | Executable JS configs, resolution integrations | None required for comparator; dynamic config can do anything | No target config/plugin discovery; audit pinned API |
| NetworkX | In-memory graph library; no subprocess needed | Backend dispatch can introduce alternate implementations | None for fixed local backend | Pin standard backend; no target Python code/config |
| Custom propagation | Existing worker only | Must not evaluate expressions/getters/config | None required | Existing guard plus future OS containment, deterministic budgets |
| Joern | Static analysis; frontend/JVM subprocesses documented | Query scripts/plugins/frontend-specific behavior | Installs/downloads must be excluded | Audit selected frontend, process allowlist, trusted scripts, isolation |
| Grimp | Import scanning; no subprocess needed | Importable-name discovery and import hooks/parent resolution | None required | Avoid generic target import environment; audit or replace discovery |
| import-linter | Graph checking; no subprocess needed | Custom contract types can load Python | None required | Only platform-owned contracts, same discovery restrictions |
| LikeC4 | Generated DSL/export possible; builds and browser/render dependencies vary | Config/build hooks and model includes need audit | Dev/build/renderer behavior unverified | Export-only trusted workspace, no target configs, escape text/links |
| Inframap | Local HCL/state parser mode; renderer external if chosen | Input references unresolved unless safely modelled | Backend pull examples are explicitly prohibited | Local files only, no Terraform/provider/remote commands, audit sources |
| ast-grep | Built-in AST matching; native parser loading is possible | Config/rules/custom native grammars | No network needed in fixed profile | Trusted config/rules and parser allowlist |
| Semgrep CE | Local source scan; CLI invokes trusted engine processes | Config selection/remote rules must be controlled | Registry, metrics, login/CI modes | Local rules, metrics off, no credentials/egress; audited invocation |
| Checkov | Local IaC scan possible; exact subprocess behavior unverified | External Python checks and auto config | External modules/platform metadata/downloads | No external checks/modules/downloads/API keys; audit pinned config path |
| Typings | Parse read-only declaration text in worker | No target plugins, compiler services or arbitrary archive paths | Fetch only through separate curated metadata maintenance | No job-time network/install; verified metadata paths and byte limits |

Static parsing is necessary but insufficient for safety. Any unresolved execution/discovery surface blocks default integration. Source evidence can contain secrets; minimize retained text, avoid logging snippets and isolate failure output as well as successful results.

## Qualitative cost estimates

L/M/H mean relative incremental burden for this codebase. Security is the integration surface before audited isolation, not a vulnerability rating. Value refers to application-architecture reconstruction, unless noted. No runtime measurements were taken.

| Addition/profile | Integration | Runtime | Memory | Maintenance | Security | Architecture value | Reason |
|---|---|---|---|---|---|---|---|
| Syft optional directory scan | M | M | M | M | M | L now | Additional full scan and package reconciliation; improves inventory |
| dependency-cruiser comparator | M | M | M | M | H with default discovery | L default / M evaluation | Repeats parsing; improves disagreement detection, not missing semantics |
| NetworkX filtered clustering | M | M | M | M | L fixed backend | Uncertain M | Duplicate graph allocation and heuristic tuning |
| Bounded propagation | H | M | M | H | M | H selected cases | State/summary management; budgets must prevent explosion |
| Joern optional frontend | H | H | H | H | H | Potential H new language | Separate runtime, graph and source-location reconciliation |
| Grimp safe comparator | M | M | M | M | M/H discovery | M imports | Independent import scan, safety wrapper effort |
| import-linter trusted contracts | M | L/M | M | M | H untrusted contracts | L reconstruction | Governance requires supplied rules |
| LikeC4 optional export | M | L generation / M render | L/M | M | M | L analysis / M sharing | Additional renderer/schema mapping |
| Inframap optional input | M/H | M | M | M/H | M pending audit | M infrastructure | Address/location recovery and provider pruning |
| ast-grep selected patterns | M | M | L/M | M | H custom native grammar | M narrow patterns | More rules and reconciliation, no full resolution |
| Semgrep CE selected rules | M | M | M | M | M | L/M | Second scan/engine; architecture rules still custom |
| Checkov diagnostics | M | M | M | M/H | H external features | L architecture | Adds security scope, not source relationship recovery |
| Curated typings | M | L/M | M | M/H | M | M | Compiler load plus version/provenance curation |

Adding all scanners multiplies parser caches, formats, timeouts and failure paths. More agreeing tools are not automatically more independent evidence. Failures must be distinguishable from empty findings; optional-provider failures should report reduced coverage, never publish a falsely complete analysis.

## Explicit answers to the final questions

1. **Material improvements:** correct value handling, framework/context semantics and responsibility/resource interpretation. Curated typings can help selected external API identities. Independent comparators improve evaluation rather than directly improving diagrams.
2. **Mostly complexity now:** default Joern alongside TS, default dependency-cruiser alongside imports, unfiltered NetworkX clustering, SBOM packages in the main diagram, and a second live LikeC4 model.
3. **Build ourselves:** bounded abstract-value tracking, semantic ownership rules, evidence derivations, reconciliation policy and architecture projection selection. Reuse compiler/parser infrastructure instead of building a new parser.
4. **Keep:** ingestion protections, no target execution/install, compiler worker, citations, unknowns, single saved graph, bounded exploration, React Flow/ELK and regression suite.
5. **Next phase:** correctness fixtures and architecture semantics for current TS/JS stacks, then an answer-first overview validated with unfamiliar users.
6. **Avoid:** full-program JavaScript promises, naming-based resource links, runtime sequence claims, untrusted executable config, automatic target installs, broad tool rollout and language-count-driven expansion.
7. **Ideal architecture:** current modular monolith plus a small normalized-finding boundary and internal interpretation/reconciliation stage. See [revised proposal](revised-architecture-proposal.md), [gap assessment](analysis-gap-assessment.md) and [roadmap](implementation-roadmap.md).
