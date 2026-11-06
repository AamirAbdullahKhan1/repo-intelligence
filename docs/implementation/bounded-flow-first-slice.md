# Bounded flow, evidence and capability slice — 4 November 2026

Implemented the first integrated slice from the approved sequence. This is not completion of every framework or a measured TS/JS accuracy claim.

## Result on the pinned GitDiagram snapshot

Fresh result: `b9306863eb1c2ec76371f9232e113e08956f567cb1151adc46e279eb9b8a5af2`, added to application history. Historical scans were not deleted, overwritten or reanalyzed in place.

| Measure | Prior saved baseline | New result |
|---|---:|---:|
| Parsed TS/JS files | 412 | 412 |
| Compiler implementation calls | 4,417 | 4,417 |
| Supported callback edges | 191 | 191 |
| Concrete/logical resource-operation links | 0 | 24 caller-context claims covering 10 distinct operation/destination pairs |
| Logical storage configuration references recovered | 0 through source operations | 2: R2_PUBLIC_BUCKET, R2_PRIVATE_BUCKET |
| Route-based capability slices | None | 19 |
| Capability-to-resource relationships | None | 10 |
| Default overview | Technical roles | 15 nodes / 17 edges; omitted slices explicitly reported |
| Demanded flow analysis | Expression recursion | 849 cells / 848 dependency steps; no flow budget exhausted on this run |

One analysis took 42.328 seconds. This is one local wall-time observation, not a statistically established performance or enterprise capacity result. Call/import/HTTP unknowns remain 3,311 / 53 / 60. Four resource unknown records explicitly retain unsupported or unknown destination contexts.

The generation capability has inspectable paths such as:

```text
POST /api/generate/stream
 → POST → stream start callback → run
 → finalizeGenerationStream → persistGenerationResult
 → saveSuccessfulDiagramState → writeDiagramArtifact
 → supported callback → putJsonObject
 → logical R2_PUBLIC_BUCKET / R2_PRIVATE_BUCKET reference
```

These are possible static paths, not a promised execution sequence. Branch feasibility and deployed account/bucket values are not established. The exact path lists are in `output/bounded-flow-review/generation-storage-paths.json`.

## Implementation

- `flow.cjs`: demand-built monotone worklist, allocation identities, module/export access paths, arguments/returns, object properties, renamed destructuring, supported await unwrapping, symbolic environment keys and cached `??=` alternatives. Call contexts distinguish factory arguments. Indexed reassignment, simple alias mutation and dynamic scopes invalidate unsupported identities. Budgets bound cells, steps, updates, candidates, contexts and time; exhaustion produces partial status and reasons. Unrelated literal flow values are serialized as identities rather than raw strings.
- `s3-flow.cjs`: bound S3Client and supported command allocations, receiver-to-command-to-Bucket flow, logical source configuration references, contextual operation claims and explicit abstentions. Uses neither repository-specific paths nor GitDiagram function names. A symbolic bucket reference is not equated with a deployed cloud resource.
- Existing expression resolver, direct resource adapters and compiler/callback extraction remain. Jelly remains isolated research tooling; it is not a production dependency.
- Canonical optional `flow_analysis` stores source-backed cells and dependency steps. Resource claims retain root/step IDs, provider, derivation version and caller context. Validation rejects missing/dangling/disconnected support and malformed capability paths.
- `capabilities.py`: route-prefix technical slices over supported calls and callbacks, shared implementation membership, original member IDs and explicit bounded paths. Resource aggregation uses the matching caller context, so two routes sharing a helper do not automatically inherit each other's buckets. Labels describe public interfaces; business capabilities are not invented.
- New graphs have a separate optional `capability_architecture`; legacy role groups and source ownership remain available. Projections prefer the new model for fresh scans, preserve canonical IDs, bound the overview and keep deployment declarations separate. Snapshot engine fingerprints include the new semantic modules.
- A paginated flow-evidence API and inspector show dependency kinds with source locations. Evidence is loaded on demand. Existing saved graphs without flow/capability fields remain readable.

## Verification

- **98 backend tests passed**, including ten new flow/resource/capability tests; two pre-existing warnings remain.
- Frontend TypeScript check and production build passed.
- Browser acceptance passed across all six tabs, canonical node/edge identities, source citations, resource value-flow evidence, component workflow selection and saved-analysis reopening; no browser errors or new analysis submissions.
- Independent fixtures cover async cached SDK imports, returned clients, symbolic configuration, factory-call separation, same-name local impostors, receiver/alias mutation, local process shadowing, eval rejection, recursion/partial reporting, corrupt evidence paths, pagination and two routes using different buckets.
- Deterministic repeated analysis is checked on the async cached-resource fixture and the complete pinned GitDiagram input. The latter produced byte-identical canonical JSON (SHA-256 `36288960798483a2b82b89019fea4832765fb8205cf3896dd77cf33b3b004162`). Independently reviewed multi-repository precision/recall remains further validation work.
- Source inspection checked the actual cached S3 factory, command construction, bucket configuration helper and generation-to-persistence call paths. Graph reference validation alone is not claimed as semantic proof.

## Scope and remaining work

This first flow consumer is S3-compatible object-storage operations. PostgreSQL/Redis retain their existing narrow adapters; they have not all migrated to the worklist. Redis coordination through HTTP/config wrappers remains a priority. Account/endpoint reconciliation and associations to declared cloud resources remain distinct from symbolic bucket references.

The solver does not implement full CFG/reaching-definitions or path-sensitive heap analysis. Arbitrary alias effects, external mutations, reflective code, general Promise combinators, arbitrary callback forwarding and unknown property keys remain incomplete. Candidate and context bounds are explicit. Preserve uncertainty rather than treating this subset as universal analysis.

Capability slices currently anchor on known routes. They do not yet recover all worker/application entry kinds, unique business-domain boundaries, branch-aware stage workflows or cross-package deployment topology. Shared membership and limits are exposed; reducing the old Other group is not used as an accuracy score.

The next integrated slice should recover the Redis coordination chain, add operation/stage labels using supported facts, and validate the same mechanisms on Express, separated frontend/API, workspaces and Workers plus an unfamiliar holdout. Proposed 95% precision / 90% recall targets remain unmeasured release goals.

Artifacts: `output/bounded-flow-review/scorecard.json`, `system.json`, `generation-storage-paths.json`, and browser screenshots/results under `output/frontend-review`. The preserved prior overview is `output/bounded-flow-review/before-overview.png`.
