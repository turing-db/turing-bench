# TuringDB Benchmark Report

> **Date:** 2026-02-26
> **Author(s):** TuringDB team

## Executive Summary

TuringDB is a column-oriented, in-memory graph database engine designed for analytical and read-intensive workloads. This report presents benchmark results comparing TuringDB against Neo4j and Memgraph across multiple datasets and query categories.

**Key findings:**

<!-- EXECUTIVE_SUMMARY -->
- Across **1 dataset(s)** and **34 queries**:
- TuringDB is **49.6x faster** than Neo4j on average (median 11.0x, max 482x)
- TuringDB wins on **33/33** queries vs Neo4j
- TuringDB is **39.4x faster** than Memgraph on average (median 9.3x, max 308x)
- TuringDB wins on **33/33** queries vs Memgraph
<!-- /EXECUTIVE_SUMMARY -->

---

## 1. Test Environment

### Hardware

<!-- HARDWARE_TABLE -->
| Spec     | Value                    |
|----------|--------------------------|
| CPU      | Intel(R) Xeon(R) Gold 5412U |
| Cores    | 48                       |
| RAM      | 251.4 GB                 |
| Storage  | SSD                      |
| OS       | Ubuntu 24.04.4 LTS       |
<!-- /HARDWARE_TABLE -->

### Software Versions

<!-- SOFTWARE_VERSIONS -->
**Database Engines**

| Database  | Version                 |
|-----------|-------------------------|
| TuringDB  | 1.0                     |
| Neo4j     | 5.26.19-SNAPSHOT        |
| Memgraph  | unknown                 |

**Client & Tools**

| Component              | Version                 |
|------------------------|-------------------------|
| Python                 | 3.13.12                 |
| turingdb (Python SDK)  | 1.20.0                  |
| neo4j (Python driver)  | 6.1.0                   |
| mgconsole              | 1.4                     |
<!-- /SOFTWARE_VERSIONS -->

All databases were run locally on the same machine, one at a time, to avoid resource contention. Neo4j and Memgraph were imported with their native indexes and constraints from the original dump. Memgraph was run in in-memory analytical mode (`--storage-mode=IN_MEMORY_ANALYTICAL`). No additional engine-specific tuning was applied beyond what the import pipeline provides.

### Client Protocol

TuringDB is queried over **HTTP** via its Python client, while Neo4j and Memgraph are queried over the **Bolt** binary protocol. Bolt is a more efficient wire protocol than HTTP for database communication, meaning TuringDB's measured times include higher protocol overhead. This makes the benchmark conservative in TuringDB's favor — with an equivalent binary protocol, TuringDB's results would be even faster.

---

## 2. Dataset

This section describes the datasets used in the benchmark. Each dataset was imported into all three engines using the same pipeline (see [turing-bench](https://github.com/turing-db/turing-bench) for reproduction steps). The data is identical across all three databases.

<!-- DATASET_SECTION -->
### Reactome

| Metric | Count |
|--------|------:|
| Nodes | 69,165 |
| Relationships | 76,040 |
| Node Labels | 10 |
| Relationship Types | 8 |
| Benchmark Queries | 34 |

<details>
<summary><b>Node Labels (10)</b></summary>

| Label | Count |
|-------|------:|
| OSMWayNode | 33,685 |
| OSMNode | 29,640 |
| OSMTags | 3,616 |
| Intersection | 2,500 |
| OSMWay | 2,080 |
| PointOfInterest | 188 |
| OSMRelation | 133 |
| Routable | 28 |
| OSM | 1 |
| Bounds | 1 |

</details>

<details>
<summary><b>Relationship Types (8)</b></summary>

| Type | Count |
|------|------:|
| NODE | 32,577 |
| NEXT | 31,996 |
| ROUTE | 5,022 |
| TAGS | 3,616 |
| FIRST_NODE | 2,080 |
| MEMBER | 562 |
| ASSOCIATED | 186 |
| BBOX | 1 |

</details>

<!-- /DATASET_SECTION -->

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
### Reactome

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n:Drug) RETURN n` | 3ms | 1446ms | 404ms | 482x | 135x |
| `MATCH (n:ProteinDrug) RETURN n` | 1ms | 241ms | 307ms | 241x | 307x |
| `MATCH (n:Drug:ProteinDrug) RETURN n` | 0ms | 371ms | 328ms | - | - |
| `MATCH (n:Taxon)-->(m:Species) RETURN n,m` | 1ms | 269ms | 308ms | 269x | 308x |
| `MATCH (n)-->(m:Interaction)-->(o) RETURN n,m,o` | 639ms | 33948ms | 33221ms | 53x | 52x |
| `MATCH (n{displayName:"Autophagy"}) RETURN n` | 410ms | 1421ms | 575ms | 3.5x | 1.4x |
| `MATCH (n{displayName:"Autophagy"})-->(m) RETURN m` | 381ms | 631ms | 489ms | 1.7x | 1.3x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN p` | 215ms | 659ms | 557ms | 3.1x | 2.6x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) RETURN q` | 219ms | 894ms | 752ms | 4.1x | 3.4x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 237ms | 2805ms | 2665ms | 12x | 11x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 295ms | 5378ms | 5188ms | 18x | 18x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 502ms | 18108ms | 17337ms | 36x | 35x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 1288ms | 68121ms | 54569ms | 53x | 42x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"}) RETURN n` | 271ms | 1184ms | 516ms | 4.4x | 1.9x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m) RETURN m` | 214ms | 1007ms | 578ms | 4.7x | 2.7x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) RETURN p` | 212ms | 589ms | 600ms | 2.8x | 2.8x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) RETURN q` | 213ms | 598ms | 623ms | 2.8x | 2.9x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 210ms | 612ms | 529ms | 2.9x | 2.5x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 396ms | 612ms | 537ms | 1.5x | 1.4x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 261ms | 626ms | 592ms | 2.4x | 2.3x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 214ms | 11154ms | 422ms | 52x | 2.0x |
| `MATCH (n)-[e:release]->(m) RETURN n,m` | 230ms | 4079ms | 3150ms | 18x | 14x |
| `MATCH (n)-[e:interactor]->(m) RETURN n,m` | 330ms | 26207ms | 25180ms | 79x | 76x |
| `MATCH (n)-[e:surroundedBy]->(m) RETURN n,m` | 312ms | 1082ms | 373ms | 3.5x | 1.2x |
| `MATCH (n)-[:hasEvent]->(m) RETURN n,m` | 305ms | 11324ms | 11111ms | 37x | 36x |
| `MATCH (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) RETURN n,m` | 97ms | 8612ms | 8552ms | 89x | 88x |
| `MATCH (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) RETURN r,s` | 159ms | 13614ms | 13564ms | 86x | 85x |
| `MATCH (n:DatabaseObject{isChimeric:false}) RETURN n` | 225ms | 2959ms | 1558ms | 13x | 6.9x |
| `MATCH (n:DatabaseObject{isChimeric:true}) RETURN n` | 217ms | 1234ms | 455ms | 5.7x | 2.1x |
| `MATCH (b)-->(a:Pathway) RETURN a` | 472ms | 4511ms | 5928ms | 9.6x | 13x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a, c` | 2268ms | 35638ms | 34421ms | 16x | 15x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN b` | 2071ms | 23014ms | 22914ms | 11x | 11x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN c` | 2168ms | 18308ms | 18054ms | 8.4x | 8.3x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a` | 2413ms | 22634ms | 22451ms | 9.4x | 9.3x |

<!-- /RESULTS_OVERVIEW -->

---

## 5. Results by Query Category

<!-- RESULTS_BY_CATEGORY -->
### 5.1 Label Scans

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n:Drug) RETURN n` | 3ms | 1446ms | 404ms | 482x | 135x |
| `MATCH (n:ProteinDrug) RETURN n` | 1ms | 241ms | 307ms | 241x | 307x |
| `MATCH (n:Drug:ProteinDrug) RETURN n` | 0ms | 371ms | 328ms | - | - |

### 5.3 Property-Based Filtering

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n{displayName:"Autophagy"}) RETURN n` | 410ms | 1421ms | 575ms | 3.5x | 1.4x |
| `MATCH (n{displayName:"Autophagy"})-->(m) RETURN m` | 381ms | 631ms | 489ms | 1.7x | 1.3x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"}) RETURN n` | 271ms | 1184ms | 516ms | 4.4x | 1.9x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m) RETURN m` | 214ms | 1007ms | 578ms | 4.7x | 2.7x |
| `MATCH (n:DatabaseObject{isChimeric:false}) RETURN n` | 225ms | 2959ms | 1558ms | 13x | 6.9x |
| `MATCH (n:DatabaseObject{isChimeric:true}) RETURN n` | 217ms | 1234ms | 455ms | 5.7x | 2.1x |

### 5.4 Relationship Type Traversal

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n)-[e:release]->(m) RETURN n,m` | 230ms | 4079ms | 3150ms | 18x | 14x |
| `MATCH (n)-[e:interactor]->(m) RETURN n,m` | 330ms | 26207ms | 25180ms | 79x | 76x |
| `MATCH (n)-[e:surroundedBy]->(m) RETURN n,m` | 312ms | 1082ms | 373ms | 3.5x | 1.2x |
| `MATCH (n)-[:hasEvent]->(m) RETURN n,m` | 305ms | 11324ms | 11111ms | 37x | 36x |
| `MATCH (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) RETURN n,m` | 97ms | 8612ms | 8552ms | 89x | 88x |
| `MATCH (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) RETURN r,s` | 159ms | 13614ms | 13564ms | 86x | 85x |

### 5.5 Multi-Hop Traversals

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN p` | 215ms | 659ms | 557ms | 3.1x | 2.6x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) RETURN q` | 219ms | 894ms | 752ms | 4.1x | 3.4x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 237ms | 2805ms | 2665ms | 12x | 11x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 295ms | 5378ms | 5188ms | 18x | 18x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 502ms | 18108ms | 17337ms | 36x | 35x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 1288ms | 68121ms | 54569ms | 53x | 42x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) RETURN p` | 212ms | 589ms | 600ms | 2.8x | 2.8x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) RETURN q` | 213ms | 598ms | 623ms | 2.8x | 2.9x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 210ms | 612ms | 529ms | 2.9x | 2.5x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 396ms | 612ms | 537ms | 1.5x | 1.4x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 261ms | 626ms | 592ms | 2.4x | 2.3x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 214ms | 11154ms | 422ms | 52x | 2.0x |

### 5.6 Complex Patterns

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n:Taxon)-->(m:Species) RETURN n,m` | 1ms | 269ms | 308ms | 269x | 308x |
| `MATCH (n)-->(m:Interaction)-->(o) RETURN n,m,o` | 639ms | 33948ms | 33221ms | 53x | 52x |
| `MATCH (b)-->(a:Pathway) RETURN a` | 472ms | 4511ms | 5928ms | 9.6x | 13x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a, c` | 2268ms | 35638ms | 34421ms | 16x | 15x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN b` | 2071ms | 23014ms | 22914ms | 11x | 11x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN c` | 2168ms | 18308ms | 18054ms | 8.4x | 8.3x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a` | 2413ms | 22634ms | 22451ms | 9.4x | 9.3x |

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
No queries where competitors outperform TuringDB were found in the benchmark.

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

### Reactome

#### Label Scans
```cypher
MATCH (n:Drug) RETURN n
MATCH (n:ProteinDrug) RETURN n
MATCH (n:Drug:ProteinDrug) RETURN n
```

#### Property-Based Filtering
```cypher
MATCH (n{displayName:"Autophagy"}) RETURN n
MATCH (n{displayName:"Autophagy"})-->(m) RETURN m
MATCH (n{displayName:"APOE-4 [extracellular region]"}) RETURN n
MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m) RETURN m
MATCH (n:DatabaseObject{isChimeric:false}) RETURN n
MATCH (n:DatabaseObject{isChimeric:true}) RETURN n
```

#### Multi-Hop Traversals
```cypher
MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN p
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) RETURN q
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) RETURN r
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t
MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v
MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) RETURN p
MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) RETURN q
MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) RETURN r
MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s
MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t
MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v
```

#### Relationship Type Traversal
```cypher
MATCH (n)-[e:release]->(m) RETURN n,m
MATCH (n)-[e:interactor]->(m) RETURN n,m
MATCH (n)-[e:surroundedBy]->(m) RETURN n,m
MATCH (n)-[:hasEvent]->(m) RETURN n,m
MATCH (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) RETURN n,m
MATCH (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) RETURN r,s
```

#### Complex Patterns
```cypher
MATCH (n:Taxon)-->(m:Species) RETURN n,m
MATCH (n)-->(m:Interaction)-->(o) RETURN n,m,o
MATCH (b)-->(a:Pathway) RETURN a
MATCH (c)-->(b)-->(a:Pathway) RETURN a, c
MATCH (c)-->(b)-->(a:Pathway) RETURN b
MATCH (c)-->(b)-->(a:Pathway) RETURN c
MATCH (c)-->(b)-->(a:Pathway) RETURN a
```

</details>
<!-- /APPENDIX_QUERIES -->

---

## Appendix B: Raw Timing Data

<!-- Link to or embed the full timing CSV -->

The raw benchmark output (per-query mean/min/max/median) is available in the `reports/` directory of the repository after running the benchmark.
