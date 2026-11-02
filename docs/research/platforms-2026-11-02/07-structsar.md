# StructSAR and related architecture-recovery research

Date: 2 November 2026. Source pinned to `sse-lnu/StructSAR@6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a`. Python files/configuration were read as text, never imported or run. No ML training, pickle loading or dependency extraction was executed. [Workflow](workflows/structsar.mmd).

## Research question and product scope

StructSAR is a replication/experiment package for file-to-module recovery, not a GitHub-to-architecture web application. Its primary analytical input is a file dependency graph and optional folder structure. Its output is a partition of files into modules, embeddings, evaluation metrics and timings.

The associated 2026 paper studies eleven Java/C/C++ systems and compares dependency-only versus folder-aware representation learning. Its finding is that structural context matters and no method wins on every system/metric; better clustering is not equivalent to reconstructing resource/network semantics. These results do not benchmark our JS/TS engine. [Paper and publication](https://journals.uio.no/NMI/article/view/13153), [full text](https://journals.uio.no/NMI/article/view/13153/11070).

## Verified processing workflow

[`run_experiments.py`](https://github.com/sse-lnu/StructSAR/blob/6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a/src/structsar/run_experiments.py) loads experiment/data configuration, prepares graph representations, trains selected embedding methods, invokes clustering, evaluates when labels exist, and records assignments/runtime. It can emit assignments without evaluation. It does not implement our full discovery/symbol/route/client pipeline.

[`preprocess_pipeline.py`](https://github.com/sse-lnu/StructSAR/blob/6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a/src/structsar/preprocessing/preprocess_pipeline.py) cleans existing CSV data and includes rebuilding helpers for earlier dependency/model outputs. Its legacy model loader uses pickle for some files; this must never become an upload parser in our application. The README identifies Depends as an upstream source of static dependencies; that extraction's correctness and execution constraints require separate review before use.

## Graphs and learned representations

[`homogeneous_graph.py`](https://github.com/sse-lnu/StructSAR/blob/6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a/src/structsar/data_builders/homogeneous_graph.py), `build_file_graph`, normalizes paths, deduplicates file nodes and dependency rows, filters endpoints to retained files and builds undirected adjacency. Module labels, when available, are collected for evaluation. Direction/detail can be lost when simplifying the dependency graph.

[`heterogeneous_graph.py`](https://github.com/sse-lnu/StructSAR/blob/6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a/src/structsar/data_builders/heterogeneous_graph.py) adds folder identities and folder/file containment, removing selected common path tokens. Model alternatives include node2vec/MetaPath2Vec and homogeneous/heterogeneous graph-attention encoders with link-reconstruction objectives. [`homogeneous_gat.py`](https://github.com/sse-lnu/StructSAR/blob/6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a/src/structsar/models/homogeneous_gat.py) contains neural message passing, positional features and minibatch-related code. These are machine-learning methods even though they do not require an LLM.

File paths are graph identities; learned clusters are output identities, not service/deployment identities. The input dependency type can be preserved in typed variants but merged in others. There is no established source-range evidence chain for a claim such as a particular client using a particular database. A module-to-module edge would aggregate existing dependencies, not create proven communication.

## Clustering and evaluation

[`clusterer.py`](https://github.com/sse-lnu/StructSAR/blob/6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a/src/structsar/eval/clusterer.py) supports KMeans/agglomerative clustering, exact cluster counts and silhouette-based count search. Search samples up to a bounded number of embeddings; exact-k experiments must be distinguished from automatically choosing the number of modules on an unknown repository. The runner seeds supported random sources, but reproducibility across hardware/library versions still requires qualification.

[`evaluation.py`](https://github.com/sse-lnu/StructSAR/blob/6157b5cc8cff0dac4262f430fdeb9ba20e9faf7a/src/structsar/eval/evaluation.py) evaluates MoJoFM, a2a, c2c coverage thresholds, ARI and optional TurboMQ. These measure different properties: agreement with a reference partition versus structural cohesion/modularity. A high structural score does not prove correct endpoint/resource edges, and a good reference alignment score depends on the chosen reference architecture.

Do not quote published extraction/learning runtime as end-to-end time to analyze a fresh enterprise ZIP. Preprocessed dependency data, graph building, training, clustering and source extraction are different costs. Minibatching, caches and stage timing are useful engineering examples; no memory/performance experiment was reproduced here.

## Architecture and UX boundaries

The recovered architecture is a flat module partition. It does not label business responsibility, detect frontend/server context, extract routes or reconstruct cloud networks. There is no inspected progressive interactive application UI. Results can support a later visualization, but they do not replace our interpretation/view builder.

Unresolved symbols omitted by the upstream dependency extractor cannot be recovered from clustering alone. Folder priors can improve alignment while also reproducing misleading folder organization. Statistical learning needs seed/model/version provenance and cannot be called the same deterministic rule system as our current core.

## Related research and application to us

[Layer recovery with ego networks](https://arxiv.org/html/2106.03040) offers a non-neural dependency-neighborhood/layering reference, but its Java closed-layer setting is narrower than arbitrary applications. The [microservice recovery comparison](https://link.springer.com/article/10.1007/s10664-025-10686-2) examines component/connection/endpoint extraction, a different task from partition agreement. Both help us separate evaluation objectives.

We already have dependency edges and ownership groups. We lack measured grouping quality. Adopt labelled partitions and multiple evaluation dimensions, plus typed-edge discipline. Defer neural clustering as a core dependency: it does not solve wrong variables, missing files/routes or configured destinations. If grouping remains weak after semantic rules, compare a simple deterministic baseline against a restricted structural experiment. Never promote a cluster to a service or claim a folder-aware embedding proves application responsibility.
