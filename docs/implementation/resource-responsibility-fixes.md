# Resource linking and technical responsibility groups

Implemented 2 November 2026. These are bounded static rules, not complete resource recovery or business architecture inference.

## Resource links

The TypeScript worker now has a trusted resources adapter. It distinguishes configuration declarations from source operations:

- **Cloudflare R2:** connect an existing Wrangler ENTRYPOINT to an inline default-export Worker fetch handler, bind its second parameter by compiler symbol, and match direct env.BINDING operations to that entry's R2 declaration/profile. Evidence includes the operation, environment parameter, configured entry, binding name and bucket. Duplicate targets within one profile remain ambiguous. Other files with an unrelated env parameter are not matched.
- **PostgreSQL:** recognize named external pg Pool/Client constructors, supported inline connectionString options and direct query operations on the bound client variable.
- **Redis:** recognize external redis createClient with supported inline URL options and selected direct operations.

URL credentials are not serialized into resource identity/labels. A known SDK/library import is not independently a datastore connection. Missing/dynamic connection options produce resource unknowns for recognized operations. Reassigned receivers, direct property replacement/deletion/update, and direct eval/with files are rejected by this narrow model. No application code, configuration plugin or connection is executed.

All USES_RESOURCE edges remain conditional static relationships. A declared bucket alone produces BINDS_RESOURCE, not USES_RESOURCE. A constructor alone does not establish an operation.

## Responsibility interpretation

A separate Python pass derives broad technical roles from canonical facts: API handling, client-side requests, database access, object storage access, cache/messaging and selected AI/payment/email/library integrations. Directory names do not assign these roles. Unsupported/unclassified entities stay under Other analyzed source.

Original entity IDs, component ownership and source relationships remain intact. Derived component records preserve full member IDs, source support edge IDs, evidence and all observed roles. One documented role priority selects primary diagram membership when a symbol has several responsibilities. This is a deterministic partition for presentation, not proof of a separate service or domain boundary.

The source overview now uses these groups on new analyses. Projections aggregate typed supporting edges without upgrading ambiguity. Groups expand through existing hierarchy/candidate/workflow APIs. Resource operations are traversable in workflows. Selecting a group/edge retrieves its canonical evidence. Default overview payloads omit full membership arrays and bound provenance previews to 20 items; complete membership/provenance stays in the saved graph.

The frontend labels these as Derived responsibility and distinguishes resource operations. Existing folder-level exploration remains available, with its previous UI/server guesses replaced by an honest directory-ownership label. No general UI redesign or database migration was added.

## Verification

Six real-pipeline regression tests cover R2 source/config correlation, unrelated env objects, unused declarations, mutation, duplicate bindings, PostgreSQL/Redis receiver identity, credential omission, unknown destinations, folder-name negatives, evidence, deterministic reruns, bounded overview, workflow traversal and SQLite save/reopen.

The full backend suite passes **80 tests**. Frontend TypeScript checking and production build pass. Existing warnings concern AnyIO's deprecated TestClient alias, an intentionally duplicated ZIP member, and npm configuration options.

The existing GitDiagram verification ZIP was scanned without executing it. It still parses 412 source files with zero syntax failures. It yields 11 broad role groups; an 18-node overview has 30 aggregated relationships. Canonical analysis, overview, summary and a verification SQLite database are in output/resource-responsibilities/. Saved-analysis reopening was checked.

**Important negative result:** the narrow resource rules establish zero concrete source-to-resource links in this GitDiagram snapshot. Its R2 code uses dynamic SDK imports, returned/destructured client objects and helper wrappers; Redis uses a custom HTTP wrapper and environment helper. Those patterns require bounded function/object/configuration summaries. Zero links/unknowns from the current resource adapter does not mean those integrations are absent; it means these access patterns fall outside its recognized models. The role groups also leave much code unclassified rather than manufacturing domain labels.

Historical saved analyses are not rewritten. Run a new analysis to use these passes; the verification database is separate from the active application's saved history.

## Remaining boundaries

- No general points-to, object mutation/escape, interprocedural resource flow or wrapper discovery.
- No @upstash/redis, Prisma, SQLAlchemy, S3 command/client reconstruction, env helper summaries or live connection validation in this pass.
- R2 configuration support remains JSON/JSONC; no TOML, generated-entry recovery or implicit imported-worker handler inference.
- Grouping captures technical responsibility, not authentication/payment/video domain workflows inferred from names.
- Node budgets can omit role groups/destinations; truncation is reported and source evidence remains accessible.
- Enterprise performance and architectural precision remain unbenchmarked. Test counts and graph counts are not accuracy percentages.

The next resource-specific task is explicit bounded summaries for configuration helpers and returned client/object shapes, verified on unfamiliar fixtures before applying them to GitDiagram's wrappers.

## Primary references

- [Cloudflare Worker fetch environment](https://developers.cloudflare.com/workers/runtime-apis/handlers/fetch/)
- [R2 binding operations](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/)
- [node-postgres Client configuration](https://node-postgres.com/apis/client)
- [node-redis connection options](https://redis.io/docs/latest/develop/clients/nodejs/connect/)

These documents supply supported API conventions; the grouping/projection policy is our own deterministic design.
