# TuringDB Benchmark Report

> **Date:** YYYY-MM-DD
> **Author(s):** TuringDB team

## Executive Summary

TuringDB is a column-oriented, in-memory graph database engine designed for analytical and read-intensive workloads. This report presents benchmark results comparing TuringDB against Neo4j and Memgraph across multiple datasets and query categories.

**Key findings:**

<!-- EXECUTIVE_SUMMARY -->
- TuringDB is **Nx faster** than Neo4j and **Nx faster** than Memgraph on average across all queries
- {Highlight 1: e.g., "On deep multi-hop traversals (4+ hops), TuringDB achieves up to 51x speedup over Neo4j"}
- {Highlight 2: e.g., "Label scans with property filters show consistent 5-10x improvements"}
- {Highlight 3: note any queries where competitors are faster, and why}
<!-- /EXECUTIVE_SUMMARY -->

---

## 1. Test Environment

### Hardware

<!-- HARDWARE_TABLE -->
| Spec     | Value                    |
|----------|--------------------------|
| CPU      | {e.g., AMD EPYC 7313P}  |
| Cores    | {e.g., 32}               |
| RAM      | {e.g., 125.4 GB}         |
| Storage  | {e.g., SSD}              |
| OS       | {e.g., Ubuntu 22.04 LTS} |
<!-- /HARDWARE_TABLE -->

### Software Versions

| Database  | Version                 |
|-----------|-------------------------|
| TuringDB  | {version}               |
| Neo4j     | {version, e.g., 5.x community} |
| Memgraph  | {version}               |

All databases were run locally on the same machine, one at a time, to avoid resource contention. Neo4j and Memgraph were imported with their native indexes and constraints from the original dump. Memgraph was run in in-memory analytical mode (`--storage-mode=IN_MEMORY_ANALYTICAL`). No additional engine-specific tuning was applied beyond what the import pipeline provides.

### Client Protocol

TuringDB is queried over **HTTP** via its Python client, while Neo4j and Memgraph are queried over the **Bolt** binary protocol. Bolt is a more efficient wire protocol than HTTP for database communication, meaning TuringDB's measured times include higher protocol overhead. This makes the benchmark conservative in TuringDB's favor — with an equivalent binary protocol, TuringDB's results would be even faster.

---

## 2. Dataset

This section describes the datasets used in the benchmark. Each dataset was imported into all three engines using the same pipeline (see [turing-bench](https://github.com/turing-db/turing-bench) for reproduction steps). The data is identical across all three databases.

---

## 3. Methodology

### Benchmark Design

- Each query is executed **once per engine** (cold run, no prior caching)
- Timing is measured with nanosecond precision (`time.perf_counter_ns()`) from the Python client side, including network round-trip
- All engines use the same Cypher queries, with minor syntax adaptations where necessary
- Results include the full query execution and result materialization time

### Why Cold Runs

Neo4j and Memgraph employ aggressive query result caching. After a first execution, subsequent runs of the same query return cached results in near-zero time, which does not reflect real-world analytical workload patterns where queries vary. We therefore report single cold-run timings to measure actual query processing performance.

### Execution Pipeline

For each dataset, the benchmark pipeline (`run.sh`):
1. Stops all database engines
2. Starts the first engine and loads the dataset
3. Executes all queries sequentially, recording wall-clock time per query
4. Stops the engine and repeats for the next engine
5. Generates a summary report with speedup ratios

---

## 4. Results Overview

<!-- RESULTS_OVERVIEW -->
| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|----------|-------|----------|------------------|---------------------|
| ...   | ...      | ...   | ...      | ...              | ...                 |
<!-- /RESULTS_OVERVIEW -->

---

## 5. Results by Query Category

<!-- RESULTS_BY_CATEGORY -->
### 5.1 Label Scans

**Pattern:** `MATCH (n:Label) RETURN n`

These queries scan all nodes with a given label and return them. They measure how efficiently each engine iterates over nodes of a specific type.

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|----------|-------|----------|------------------|---------------------|
| ...   | ...      | ...   | ...      | ...              | ...                 |

**Analysis:**

TuringDB's column-oriented storage gives it a structural advantage on label scans. In a traditional row-oriented engine (Neo4j, Memgraph), scanning all nodes of a label requires visiting each node record and extracting all its properties — even if the query only needs a subset. In TuringDB, nodes sharing a label are stored in contiguous columnar arrays within DataParts, enabling sequential memory access patterns that modern CPUs can prefetch efficiently. This avoids the pointer-chasing overhead inherent to adjacency-list representations.

### 5.2 Full Graph Scans

**Pattern:** `MATCH (n) RETURN n` / `MATCH ()-[r]->() RETURN r`

These queries iterate over the entire node or edge set without any filtering.

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|----------|-------|----------|------------------|---------------------|
| ...   | ...      | ...   | ...      | ...              | ...                 |

**Analysis:**

{Explain why full scans benefit from columnar layout — contiguous memory, SIMD vectorization, no index overhead.}

### 5.3 Property-Based Filtering

**Pattern:** `MATCH (n{property: value}) RETURN n` / `MATCH (n) WHERE n.property = value RETURN n`

These queries filter nodes by an exact property match. They test how efficiently each engine evaluates predicates during traversal.

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|----------|-------|----------|------------------|---------------------|
| ...   | ...      | ...   | ...      | ...              | ...                 |

**Analysis:**

{Explain. Example:}

TuringDB stores each property as a separate column, so filtering by `displayName` requires scanning only the `displayName` column — a compact, contiguous array — rather than deserializing full node records. Neo4j and Memgraph, without a dedicated index on the filtered property, must perform a full scan of node records and extract the property from each one, touching significantly more memory.

Note that Neo4j and Memgraph benefit from the indexes and constraints included in the original dataset dump. TuringDB does not use explicit indexes — its columnar layout makes property scans inherently fast without them.

### 5.4 Relationship Type Traversal

**Pattern:** `MATCH (n)-[:TYPE]->(m) RETURN n, m`

These queries traverse edges of a specific relationship type between nodes.

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|----------|-------|----------|------------------|---------------------|
| ...   | ...      | ...   | ...      | ...              | ...                 |

**Analysis:**

{Explain how TuringDB's edge storage (contiguous arrays of outgoing/incoming edges per DataPart) compares to pointer-based adjacency lists. Discuss cache locality.}

### 5.5 Multi-Hop Traversals

**Pattern:** `MATCH (start)-->(a)-->(b)-->...-->(end) RETURN end`

These queries start from a filtered node and traverse progressively deeper paths (1 to 8 hops). This is the most demanding category, as the result set can grow exponentially with each hop.

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|----------|-------|----------|------------------|---------------------|
| ...   | ...      | ...   | ...      | ...              | ...                 |

**Analysis:**

{This is the most important section. Example:}

Multi-hop traversals are where TuringDB's architecture provides the most dramatic advantage. The speedup grows with traversal depth: from ~5x at 1 hop to **51x over Neo4j** at 8 hops.

Traditional graph databases use a Volcano/iterator execution model that processes one node at a time, chasing pointers through memory for each hop. At each expansion step, the engine must:
1. Look up each frontier node's adjacency list (random memory access)
2. Follow pointers to neighbor records (cache miss)
3. Repeat for each hop level

TuringDB's streaming columnar execution processes each hop as a bulk operation over contiguous arrays. The execution engine:
1. Produces a column of frontier node IDs
2. Performs a vectorized lookup of outgoing edges (sequential memory scan)
3. Outputs the next column of neighbor IDs

This means each hop is a dense, cache-friendly array operation rather than millions of individual pointer dereferences. As hop count increases, the compounding effect of cache efficiency and SIMD vectorization produces increasingly large speedups.

### 5.6 Complex Patterns

**Pattern:** Multi-node patterns with multiple relationship types and property projections.

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|----------|-------|----------|------------------|---------------------|
| ...   | ...      | ...   | ...      | ...              | ...                 |

**Analysis:**

{Explain how the query planner handles join-like patterns, and how columnar batch processing benefits multi-condition queries.}

### 5.7 Aggregations

**Pattern:** `MATCH (...) RETURN count(n)`

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|----------|-------|----------|------------------|---------------------|
| ...   | ...      | ...   | ...      | ...              | ...                 |

**Analysis:**

{Explain how columnar storage enables fast aggregations — counting over a dense array vs. iterating node-by-node.}
<!-- /RESULTS_BY_CATEGORY -->

---

## 6. Why TuringDB Is Faster: Architectural Deep Dive

### Column-Oriented Storage vs. Row-Oriented

Traditional graph databases (Neo4j, Memgraph) use **row-oriented storage**: each node is stored as a self-contained record with all its properties and adjacency pointers. This is efficient for single-node lookups but wasteful for analytical queries that scan many nodes and only need a few properties.

TuringDB uses **column-oriented storage**: each property is stored as a separate, contiguous array. This design, proven in analytical relational databases (ClickHouse, DuckDB), is adapted here for graph workloads.

**Impact on benchmarks:**
- Label scans touch only the label column, not entire node records
- Property filters scan a single column instead of deserializing full nodes
- Aggregations (COUNT, etc.) operate on dense integer arrays

### Streaming Execution vs. Volcano Model

Neo4j and Memgraph use the **Volcano (iterator) model**: each operator in the query plan produces one row at a time, pulling from the operator below. This introduces per-row function call overhead and prevents vectorized processing.

TuringDB uses a **streaming columnar execution engine**: each operator processes a batch of values (a column) at once. This enables:
- **SIMD vectorization** — processing multiple values per CPU instruction
- **Reduced function call overhead** — one call per batch, not per row
- **Better branch prediction** — uniform operations on homogeneous data

### Zero-Locking Snapshot Isolation

TuringDB's immutable DataPart architecture means read queries never contend with writes. While this benchmark runs queries sequentially (no concurrent load), the zero-locking design means there is no lock acquisition overhead even for single queries — the engine skips the entire lock management code path.

### No Index Dependency

Neo4j and Memgraph rely on indexes to accelerate property lookups — and in this benchmark, they benefit from the indexes and constraints included in the original dataset dump. TuringDB does not use explicit index structures. Its columnar layout makes property scans inherently fast — the column itself acts as a natural "index" for scan-based access patterns. Despite the competitors having indexes available, TuringDB still outperforms them on most property filter queries.

---

## 7. Where Competitors Win

<!-- Transparency: acknowledge queries where Neo4j or Memgraph is faster -->

<!-- COMPETITOR_WINS -->
{List queries where competitors are faster, with analysis.}
<!-- /COMPETITOR_WINS -->

---

## 8. Limitations and Caveats

- **Single-machine benchmark.** All engines ran locally; distributed deployment characteristics are not measured.
- **Cold-run only.** Results reflect first-execution performance. Workloads with repeated identical queries would benefit from Neo4j/Memgraph's query caching.
- **Import-provided configuration.** Neo4j and Memgraph use the indexes and constraints from the original dump, and Memgraph runs in in-memory analytical mode. No additional tuning was applied. Production deployments may include further optimizations.
- **Client-side timing.** Measurements include Python client overhead and network round-trip (localhost). TuringDB uses HTTP while Neo4j and Memgraph use the more efficient Bolt protocol, giving the competitors a wire-protocol advantage.
- **Two datasets.** Results may not generalize to all graph structures or query patterns. Additional datasets would strengthen conclusions.
- **No concurrent load.** The benchmark runs queries sequentially with no simulated concurrent users.

---

## 9. Reproducing the Benchmark

All benchmark code, queries, and dataset import scripts are open source:

**Repository:** https://github.com/turing-db/turing-bench

```bash
git clone https://github.com/turing-db/turing-bench.git
cd turing-bench

# Install engines
./install.sh

# Set up environment
source env.sh

# Download and import dataset
./scripts/neo4j-43-imports/run_all.sh {dataset_name}

# Run full benchmark
./run.sh {dataset_name}
```

The benchmark script generates a timestamped report and optionally updates the README with a summary table.

---

## Appendix A: Full Query Listing

<!-- APPENDIX_QUERIES -->
<details>
<summary>Click to expand</summary>

### Label Scans
```cypher
MATCH (n:Label) RETURN n
...
```

### Multi-Hop Traversals
```cypher
MATCH (n{displayName:"Autophagy"})-->(m) RETURN m
MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN p
...
```

</details>
<!-- /APPENDIX_QUERIES -->

---

## Appendix B: Raw Timing Data

<!-- Link to or embed the full timing CSV -->

The raw benchmark output (per-query mean/min/max/median) is available in the `reports/` directory of the repository after running the benchmark.
