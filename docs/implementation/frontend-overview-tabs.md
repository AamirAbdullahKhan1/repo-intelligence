# Diagram-first results and separate exploration tabs

Implemented 2 November 2026. This is a presentation change over saved canonical analyses; no source-analysis passes or database schema were changed.

## Result experience

- **Architecture overview** is the initial/reopened view. It shows evidenced responsibility groups and connected SDK/resource destinations. Folder navigation, function controls and diagnostics are absent from the landing canvas. Summary/coverage is collapsed, and evidence opens only on selection.
- **Workflows** has a component selector, suggested/searchable entry points and bounded static calls. Depth remains available; additional limits, imports, nested definitions and unknown markers are under Advanced options.
- **Code explorer** retains package/directory/symbol exploration and expert graph controls.
- **Declared deployment** is explicitly separate from source usage and actual deployment state.
- **Needs context** and **Diagnostics** retain unresolved evidence and runtime/tool reporting.

The overview display subgraph excludes Other analyzed source and generic Library integration groups when specific responsibilities exist. Their original records remain accessible in deeper exploration. Individual HTTP hosts are in a separate expandable, evidence-linked list rather than creating a large fan-out on the landing diagram. No new node identity, relationship or inferred path is introduced by this filtering. Filtered groups/relationships are disclosed, and the display is capped at 16 nodes.

Labels separate responsibility from package identity. System nodes have additional vertical space for status text. Empty/error states explain next steps. Historical analyses without the responsibility model show a notice requiring a new scan instead of pretending their grouping was upgraded. Switching back to the overview resets scope and advanced dependency settings.

Storage declarations without established links remain explicitly identified as incomplete. The frontend does not fix the remaining resource-wrapper resolution gaps or infer missing AI/storage connections for visual completeness.

## Verification

TypeScript checking and the Vite production build pass. Browser acceptance in scripts/verify_result_tabs.cjs verifies all six tabs against the latest saved GitDiagram graph, component workflows, node and HTTP-host evidence, uncertainty inspection, and reopening after reload. It checks displayed node/edge IDs against the saved canonical graph and rejects browser/API errors. No new analysis was submitted and no GitDiagram code was executed.

The final focused overview contains **10 nodes** in this snapshot. Screenshots at 1600px and 1100px, workflow screenshot and machine-readable browser results are in output/frontend-review/. Screenshots were visually reviewed; initial dense helper connections led to the focused projection above. This is not a claim that the reconstructed architecture is complete.

The preview uses a separate SQLite database containing a copy of the saved verification analysis. Existing application history was not overwritten. Local preview frontend: http://127.0.0.1:5182/; preview API: http://127.0.0.1:8012/. Select the saved GitDiagram analysis if no snapshot is selected.

To repeat the browser test, set PLAYWRIGHT_MODULE to an installed Playwright package path, optionally APP_URL to the preview frontend, then run node scripts/verify_result_tabs.cjs. No dependency installation is needed in the current environment.
