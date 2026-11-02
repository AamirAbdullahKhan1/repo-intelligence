# SciTools Understand: documented technical model

Date: 2 November 2026. Commercial engine source and an executable installation were not inspected. Product mechanisms below are **Documented**, not independently reproduced. Proprietary parser algorithms, table/index layout and accuracy are **Unknown** unless a cited public document states otherwise. Workflow: [diagram](workflows/understand.mmd).

## Product and workflow

Understand serves developers investigating unfamiliar/legacy code, dependencies, metrics and change impact. Input is a configured local project/source set; output is a reusable project analysis database and many navigable views. Its underlying structure is not a generated cloud-deployment architecture.

The best-supported pipeline is: choose source files/language settings → provide compiler context → analyze → store entities/references → query/group them → show call/dependency/architecture views. A successful application build is not inherently necessary, but accurate compiler context matters. Official guidance identifies includes/import paths, macros and language/compiler variants as important; it also offers existing build metadata or build-capture workflows. We can consume supplied metadata safely, but must not run a build to obtain it. [Accuracy inputs](https://docs.scitools.com/help/projects/what-understand-needs.html).

## Parsing and incomplete projects

C/C++ has documented Strict/Clang and older tolerant Fuzzy modes. Missing context can produce unresolved or missing entities and wrong active-preprocessor choices. Fuzzy is not equivalent modern-C++ semantic precision. This does not reveal the implementation of every other language frontend. Broad language support is documented, with language-specific settings; cross-language project membership does not prove universal cross-language symbol resolution. [Parsing modes](https://docs.scitools.com/help/accuracy/accurate-c-cpp-projects.html), [languages](https://docs.scitools.com/help/getting-started/supported-languages.html).

## Single model and graph construction

An entity represents a file/function/type/variable; a reference records a connection at a source location. API types include `understand.Ent`, `Ref` and `Arch`; documented queries include `db.ents()` and `ent.refs()`, with kind filters and opposing directions such as Call/CallBy. This supports caller/callee navigation without rescanning source for each view. IDs' cross-version stability and internal indexing algorithm remain unknown. [Entity/reference API](https://docs.scitools.com/help/apis/tutorials/tutorial-3-entities-references-filters.html).

File/class/architecture dependencies are computed by grouping qualifying references through parent chains. Each aggregate retains the underlying references, allowing source drill-down. Language-specific kinds and options determine which references count; an import/dependency edge does not automatically mean network traffic. [Dependency semantics](https://docs.scitools.com/help/dependencies/what-are-dependencies.html).

This is a particularly useful precedent for our one-graph/multiple-views design: aggregate facts at the requested abstraction without deleting their meaning.

## Architecture interpretation

Understand defines architecture as a named nested grouping of files/entities, independent of directories. Automatic directory/language/build-related hierarchies, plugins and manual/custom groupings coexist. Thus a polished architecture diagram is not proof of automatic discovery of services or business responsibilities. Framework-specific routes, SDK destinations and database-instance matching are not established by these architecture documents. [Architecture model](https://docs.scitools.com/help/architecture/what-is-an-architecture.html).

Python architecture plugins can create groupings from the parsed model; they are trusted executable extensions, unsuitable for loading from client uploads. [Architecture plugins](https://docs.scitools.com/help/architecture/write-an-architecture-plugin.html).

## Database, exploration and impact

The `.und` project bundle separates project settings from regenerable parsed data; current documentation describes optional local placement of that analysis data. Its format should not be described as SQLite/Neo4j without evidence. Large parsed datasets consume disk/memory; we did not benchmark indexing or incremental invalidation. [Database](https://docs.scitools.com/help/projects/manage-und-database.html).

Impact combines changed-entity comparisons with reverse references/caller traversal to a chosen scope. The documentation explicitly describes reachability as a conservative potentially affected set, not proof that every dependent's behavior changes. Call/dependency graphs, matrices and source-reference navigation support investigation. [Impact analysis](https://docs.scitools.com/help/compare/change-impact-analysis.html).

Core parsing/navigation is not documented as requiring an LLM; optional AI features are distinct. Supported CLI/Python automation gives evidence of extensibility, not unrestricted safe processing of hostile configurations.

## Our platform comparison

We already have source entities, evidence, grouping and multiple projections. Understand offers a mature documented entity/reference query model, many languages, caller/callee/compare views and user-controlled architectures. We lack that breadth and sustained evaluation; there is no measured performance comparison.

Learn: preserve exact references under aggregates, expose reverse navigation, distinguish language settings from incomplete syntax coverage, and keep user-defined grouping separate from recovered facts. Later add a read-only query API.

Do not adopt: build capture inside our analysis, uploaded executable plugins, or an assumption that purchasing a mature parser supplies source-to-cloud architecture interpretation. Our immediate work remains resolution and configured-resource linking, not recreating Understand's full desktop suite.

## Unknowns

Proprietary resolver/alias algorithms, dynamic-dispatch precision, detailed storage/index implementation, quantitative large-repository behavior and framework resource semantics remain unverified. No trial, product demonstration session, source import or vendor benchmark was executed for this report.
