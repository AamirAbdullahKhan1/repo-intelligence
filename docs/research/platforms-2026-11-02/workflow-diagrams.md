# Workflow diagrams

Date: 2 November 2026. These are source-reconstructed or documented pipelines, not executed traces. Unknown stages are explicit. The linked individual reports explain provenance and limits.

## repodna

[Standalone Mermaid source](workflows/repodna.mmd)

```mermaid
flowchart TD
 A["GitHub revision: public web path"] --> B["Durable workflow and commit artifact cache"]
 B --> C["Archive or bounded Git-tree acquisition"]
 D["Browser ZIP or folder"] --> E["Browser analysis worker"]
 C --> F["analyzeRepositoryFiles: fingerprint and syntax extraction"]
 E --> F
 F --> G["Custom imports and name-based call resolution"]
 G --> H["Role buckets, import aggregation and bounded static flows"]
 H --> I["v1-to-v2 adaptation, analytics and artifact compaction"]
 I --> J["Validated artifact: React Flow, evidence and exports"]
 K["Separate Python CLI: AST/regex and file parse cache"] -. "different engine; same product" .-> H
```

## understand

[Standalone Mermaid source](workflows/understand.mmd)

```mermaid
flowchart TD
 A["Source project plus language/compiler settings"] --> B["Language-specific parsing: documented"]
 B --> C["Parsed entities and located references"]
 C --> D["Reusable project analysis database"]
 D --> E["Reference filtering and parent/group aggregation"]
 E --> F["Calls, dependencies, matrix and source navigation"]
 G["Automatic, plugin or user architecture grouping"] --> E
 D --> H["Version comparison and potential-impact traversal"]
 B -.-> U["Proprietary resolver and storage algorithms: unknown"]
```

## joern

[Standalone Mermaid source](workflows/joern.mmd)

```mermaid
flowchart TD
 A["Source path and selected frontend configuration"] --> B["Language frontend / trusted AST generator"]
 B --> C["AST creation and metadata/import/dependency passes"]
 C --> D["Base, control-flow, type and call-graph overlays"]
 D --> E["Optional reaching-definition/data-flow overlay"]
 E --> F["CPG with applied-layer metadata; Flatgraph storage"]
 F --> G["CPGQL traversal, flow paths and exports"]
 G -.-> H["Application architecture requires additional custom rules"]
```

## codesee

[Standalone Mermaid source](workflows/codesee.mmd)

```mermaid
flowchart TD
 A["GitHub installation and repository access: documented"] --> B["Dependency extraction engine: implementation unknown"]
 B --> C["Codebase file/folder dependency map"]
 C --> D["Collapse, focus, annotations, insights and source navigation"]
 E["Pull request and later commits"] --> F["Review Map: changed and dependent files"]
 B --> F
 F --> G["Review tours and potential-impact exploration"]
 H["Enterprise Service Map advertised"] -.-> U["Service extraction and reconciliation: unknown"]
```

## gitdiagram

[Standalone Mermaid source](workflows/gitdiagram.mmd)

```mermaid
flowchart TD
 A["GitHub repository"] --> B["Metadata, tree and README"]
 B --> C["Bounded integrity-checked source excerpts and references"]
 C --> D["AI architecture interpretation"]
 D --> E["Structured groups, nodes, edges and repository paths"]
 E --> F["Graph/path validation and repair feedback"]
 F -. "repair" .-> D
 F --> G["Deterministic graph-to-Mermaid compiler"]
 G --> H["Browser rendering/sanitization and GitHub links"]
 F --> I["Persisted artifact for reopening"]
```

## sourcegraph

[Standalone Mermaid source](workflows/sourcegraph.mmd)

```mermaid
flowchart TD
 A["Repository and project/dependency context"] --> B["Language indexer: CI or executor"]
 B --> C["SCIP index: documents, symbols, occurrences and relationships"]
 C --> D["Upload and server index processing: documented"]
 D --> E["Definitions, references and implementations"]
 F["Search-based navigation"] -. "fallback" .-> E
 B -.-> U["Indexer install/build behavior varies; must qualify"]
 E -.-> G["Architecture semantics are outside this navigation pipeline"]
```

## structsar

[Standalone Mermaid source](workflows/structsar.mmd)

```mermaid
flowchart TD
 A["Source dependency extraction upstream; not reproduced"] --> B["Dependency CSV/model records and optional ground truth"]
 B --> C["Preprocessing and file graph construction"]
 C --> D["Optional folder relations and typed dependencies"]
 D --> E["Learned embeddings: walks or graph neural models"]
 E --> F["KMeans or agglomerative module partition"]
 F --> G["Assignments and stage/runtime outputs"]
 H["Reference architecture"] --> I["MoJoFM, a2a, c2c, ARI and modularity evaluation"]
 F --> I
```
