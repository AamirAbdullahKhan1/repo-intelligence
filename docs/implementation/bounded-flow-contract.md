# Baseline and implementation contract — 4 November 2026

Baseline is the immutable GitDiagram input used by saved result `d35bbceee8a9…`: 412 parsed files, 4,417 implementation calls, 6,989 library references, 191 callback edges, 3,311 call / 53 import / 60 HTTP unknowns, zero resource-operation links, and 4,620 of 4,754 eligible entities in Other. These are coverage facts, not accuracy scores. The isolated Jelly experiment is partial and is not a production dependency.

Retain ingestion/archive safety, immutable snapshots, compiler/project resolution, existing callbacks/value resolver, SQLite, old graph records, React Flow and ELK. Extend the worker with a bounded flow subsystem and operation provider; add optional provenance fields and capability records. Old saved results are read as saved; no migration rewrites them. Changes to semantic code must enter engine fingerprints.

The first flow implementation uses allocation identities, module/export paths, function arguments and returns, object/destructuring/property flow, supported awaits, symbolic configuration and conservative cached-initializer alternatives. It is a monotone worklist with explicit candidate/cell/job/time budgets. Unknowns and unsupported mutations block confirmation. No expressions, target configuration, packages or plugins execute.

Flow records carry immutable source citations and dependency steps. Resource claims require a bound client, operation identity and bucket argument; resource declarations alone are insufficient. Symbolic destinations are logical source references, not deployed values. Branch/path completeness and arbitrary alias mutation are outside this first subset and must be reported. Different factory contexts must not become a single resolved destination.

Affected interfaces: trusted worker adapters/index; optional canonical `flow_analysis`; evidence validation; resource relationships with derivation/proof references; optional derived capability model and bounded graph projections. Additive fields are accepted by existing Pydantic records, but new invariants are validated explicitly. Preserve original entity and edge IDs. Existing tests and old saved graphs remain compatibility checks.

Delivery gates: independent positive/negative fixtures, deterministic rerun, source-backed GitDiagram operation chains, no unsupported call promotion, bounded partial-state reporting, full backend regression, frontend build and relevant browser checks. Deliver measured before/after results; do not equate larger graphs with success.

Sequence: (1) demand-built worklist and provenance together; (2) source-bound S3/client operations and symbolic resources; (3) entry-point capability slices with shared membership and complete supporting paths; (4) saved result and UI verification. Broader framework profiles, precise control-flow ordering and holdout accuracy remain separate readiness gates.
