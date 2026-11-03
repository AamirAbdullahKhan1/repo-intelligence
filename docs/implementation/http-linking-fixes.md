# Conditional frontend-to-route linking

Implemented 2 November 2026. Builds on project resolution without installing tools or running submitted application code.

## Behavior

The trusted HTTP adapter indexes supported Next app-route handlers by owning application, method and segment count. An unshadowed global fetch in a module with an actual use-client directive can produce a conditional CALLS_HTTP edge to one compatible route in the same Next package. GET defaults only when request options are absent or a supported inline options object omits method. Explicit literal/unmodified string methods are supported; spreads, computed properties, accessors, shorthand method fields and dynamic options are not guessed.

Literal root-relative paths may include query/fragment suffixes and single-segment Next parameters. Network-relative URLs, encoded paths, repeated slashes, dot segments, unknown origins, different applications and unsupported methods remain unknown. Multiple matching patterns retain candidate IDs and ambiguity instead of picking a target. Matching requires an existing HANDLED_BY relationship, not just a similarly named exported value.

Every candidate retains callsite/value evidence, client directive and route registration evidence. All links remain **conditional**: same-origin deployment, routing configuration, middleware, invocation and actual delivery have not been proved. Routing-related files are listed but never executed. Presence of a matching route is not a runtime observation.

Projections now retain resolution status when aggregating edges and SDK groups. Exploration preserves ambiguous unknowns and candidate IDs. Configuration diagnostics no longer incorrectly contribute to the syntax-failure counter.

## Verification

Five pipeline tests cover method-sensitive dynamic segments, both-end evidence, deterministic output, unknown options/methods, cross-package collisions, server-origin uncertainty, ambiguous patterns, inert malicious configuration, misplaced client directives, non-callable exports and projection status retention. Full backend suite: **74 passed**, two existing warnings.

Fresh GitDiagram verification ZIP: 412 parsed files, zero syntax failures, eight additional conditional internal HTTP links, 60 HTTP unknowns. Examples include POST /api/admin/session from admin sign-in and GET /api/sponsor from the sponsor hook. No ambiguous requests were found in this particular snapshot; fixtures cover ambiguity. The full graph and summary are in output/http-linking/. One run took 32.016 seconds, not a benchmark. Existing saved analyses were not replaced.

## Limits and next work

This is a narrow candidate linker, not complete frontend/backend resolution. Imported client-module context, request wrappers/Axios, Request objects, proxy origins, Next basePath/rewrites, Pages Router, catch-all routing and routing precedence remain unsupported. Express route mount prefixes are not modeled and are deliberately not matched as full endpoints. Dynamic-template values still require the existing bounded literal analysis to succeed.

The overview still collapses internal same-application edges at its current abstraction. Component/workflow exploration can use these canonical edges; a richer responsibility-based overview remains separate work. Resource/client/configuration linking also remains outstanding.

## Primary references

- [Fetch RequestInit](https://developer.mozilla.org/en-US/docs/Web/API/RequestInit)
- [Next dynamic segments](https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes)
- [Next rewrites](https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites)

These sources inform narrow static rules. Framework behavior beyond the supported rules is not assumed to have been analyzed.
