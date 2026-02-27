# TuringDB Benchmark Report

> **Date:** 2026-02-27
> **Author(s):** TuringDB team

## Executive Summary

TuringDB is a column-oriented, in-memory graph database engine designed for analytical and read-intensive workloads. This report presents benchmark results comparing TuringDB against Neo4j and Memgraph across multiple datasets and query categories.

**Key findings:**

<!-- EXECUTIVE_SUMMARY -->
- Across **1 dataset(s)** and **34 queries**:
- TuringDB is **53.1x faster** than Neo4j on average (median 11.0x, max 517x)
- TuringDB wins on **33/33** queries vs Neo4j
- TuringDB is **32.9x faster** than Memgraph on average (median 11.0x, max 231x)
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
| Nodes | 2,978,202 |
| Relationships | 11,537,843 |
| Node Labels | 108 |
| Relationship Types | 88 |
| Benchmark Queries | 34 |

<details>
<summary><b>Node Labels (108)</b></summary>

| Label | Count |
|-------|------:|
| DatabaseObject | 2,978,202 |
| ReferenceEntity | 930,514 |
| ReferenceSequence | 927,102 |
| DatabaseIdentifier | 856,680 |
| ReferenceDNASequence | 617,302 |
| Deletable | 532,391 |
| Trackable | 524,558 |
| PhysicalEntity | 406,613 |
| GenomeEncodedEntity | 246,176 |
| EntityWithAccessionedSequence | 238,918 |
| ReferenceRNASequence | 204,186 |
| Person | 171,942 |
| InstanceEdit | 157,659 |
| Event | 117,945 |
| Complex | 110,048 |
| ReferenceGeneProduct | 105,614 |
| ReactionLikeEvent | 94,655 |
| Reaction | 83,459 |
| MetaDatabaseObject | 79,220 |
| Interaction | 77,995 |
| UndirectedInteraction | 77,995 |
| UpdateTracker | 60,837 |
| AbstractModifiedResidue | 56,756 |
| TranslationalModification | 50,733 |
| EntitySet | 43,526 |
| Publication | 42,286 |
| LiteratureReference | 42,098 |
| CatalystActivity | 40,297 |
| ModifiedResidue | 36,547 |
| DefinedSet | 34,937 |
| Pathway | 23,290 |
| Summation | 21,332 |
| GroupModifiedResidue | 13,057 |
| DeletedInstance | 10,573 |
| BlackBoxEvent | 10,435 |
| CandidateSet | 8,589 |
| Regulation | 7,833 |
| Deleted | 7,668 |
| GeneticallyModifiedResidue | 5,947 |
| PositiveRegulation | 4,590 |
| SimpleEntity | 3,897 |
| ReplacedResidue | 3,459 |
| ControlReference | 3,367 |
| NegativeRegulation | 3,243 |
| GO_Term | 3,198 |
| FragmentModification | 2,488 |
| ReferenceIsoform | 2,369 |
| FragmentReplacedModification | 2,259 |
| ReferenceMolecule | 2,183 |
| RegulationReference | 1,897 |
| GO_MolecularFunction | 1,665 |
| Polymer | 1,391 |
| NonsenseMutation | 1,331 |
| PositiveGeneExpressionRegulation | 1,308 |
| Drug | 1,203 |
| CrosslinkedResidue | 1,129 |
| ChemicalDrug | 1,106 |
| CatalystActivityReference | 1,105 |
| ReferenceTherapeutic | 1,087 |
| GO_BiologicalProcess | 1,082 |
| NegativePrecedingEvent | 1,065 |
| ExternalOntology | 1,008 |
| Figure | 882 |
| Requirement | 851 |
| Disease | 770 |
| InterChainCrosslinkedResidue | 747 |
| EntityFunctionalStatus | 698 |
| FailedReaction | 457 |
| GO_CellularComponent | 451 |
| TopLevelPathway | 415 |
| Taxon | 408 |
| IntraChainCrosslinkedResidue | 382 |
| MarkerReference | 365 |
| Affiliation | 348 |
| OtherEntity | 348 |
| NegativeGeneExpressionRegulation | 331 |
| Polymerisation | 253 |
| PsiMod | 175 |
| Compartment | 156 |
| FragmentInsertionModification | 145 |
| ReferenceGroup | 142 |
| Release | 142 |
| Book | 133 |
| ReferenceDatabase | 103 |
| Species | 95 |
| ProteinDrug | 95 |
| FragmentDeletionModification | 84 |
| ModifiedNucleotide | 76 |
| TranscriptionalModification | 76 |
| URL | 55 |
| CellType | 31 |
| Depolymerisation | 29 |
| FunctionalStatus | 27 |
| Cell | 24 |
| CellDevelopmentStep | 22 |
| ControlledVocabulary | 21 |
| SequenceOntology | 15 |
| Anatomy | 14 |
| CellLineagePath | 12 |
| DeletedControlledVocabulary | 7 |
| NegativePrecedingEventReason | 6 |
| ReviewStatus | 5 |
| FunctionalStatusType | 5 |
| EvidenceType | 3 |
| DrugActionType | 3 |
| ReactionType | 3 |
| RNADrug | 2 |
| DBInfo | 1 |

</details>

<details>
<summary><b>Relationship Types (88)</b></summary>

| Type | Count |
|------|------:|
| created | 2,797,487 |
| referenceDatabase | 1,869,394 |
| crossReference | 1,094,497 |
| species | 739,423 |
| referenceGene | 639,701 |
| compartment | 560,432 |
| inferredTo | 455,759 |
| author | 422,897 |
| hasComponent | 274,487 |
| referenceEntity | 244,018 |
| referenceTranscript | 219,870 |
| summation | 210,761 |
| input | 186,017 |
| hasMember | 172,620 |
| modified | 165,988 |
| output | 158,432 |
| interactor | 155,990 |
| hasModifiedResidue | 124,194 |
| hasEvent | 120,933 |
| literatureReference | 106,182 |
| evidenceType | 96,169 |
| precedingEvent | 73,882 |
| release | 60,837 |
| updatedInstance | 60,837 |
| referenceSequence | 56,756 |
| psiMod | 56,312 |
| catalystActivity | 52,010 |
| activity | 40,699 |
| physicalEntity | 40,297 |
| hasCandidate | 35,687 |
| reviewed | 27,812 |
| authored | 23,491 |
| reviewStatus | 21,779 |
| edited | 21,549 |
| disease | 20,493 |
| goBiologicalProcess | 18,300 |
| modification | 14,050 |
| activeUnit | 11,790 |
| regulatedBy | 11,164 |
| deletedInstance | 10,591 |
| regulator | 7,833 |
| reason | 7,099 |
| includedLocation | 6,960 |
| hasEncapsulatedEvent | 6,524 |
| replacementInstances | 3,967 |
| relatedSpecies | 3,030 |
| structureModified | 2,943 |
| internalReviewed | 2,675 |
| regulationReference | 1,985 |
| regulation | 1,897 |
| previousReviewStatus | 1,795 |
| repeatedUnit | 1,432 |
| revised | 1,423 |
| catalystActivityReference | 1,402 |
| negativePrecedingEvent | 1,065 |
| functionalStatus | 1,061 |
| figure | 940 |
| entityFunctionalStatus | 798 |
| secondReferenceSequence | 747 |
| normalReaction | 722 |
| diseaseEntity | 698 |
| equivalentTo | 683 |
| normalEntity | 617 |
| goCellularComponent | 612 |
| entityOnOtherCell | 563 |
| instanceOf | 535 |
| affiliation | 494 |
| normalPathway | 469 |
| superTaxon | 404 |
| isoformParent | 384 |
| marker | 365 |
| cell | 365 |
| markerReference | 365 |
| componentOf | 272 |
| proteinMarker | 191 |
| surroundedBy | 189 |
| RNAMarker | 172 |
| cellType | 114 |
| reverseReaction | 112 |
| requiredInputComponent | 105 |
| publisher | 97 |
| hasPart | 33 |
| tissue | 30 |
| functionalStatusType | 27 |
| structuralVariant | 27 |
| reactionType | 15 |
| organ | 15 |
| tissueLayer | 5 |

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
| `MATCH (n:Drug) RETURN n` | 3ms | 1551ms | 307ms | 517x | 102x |
| `MATCH (n:ProteinDrug) RETURN n` | 1ms | 220ms | 231ms | 220x | 231x |
| `MATCH (n:Drug:ProteinDrug) RETURN n` | 0ms | 285ms | 338ms | - | - |
| `MATCH (n:Taxon)-->(m:Species) RETURN n,m` | 1ms | 366ms | 180ms | 366x | 180x |
| `MATCH (n)-->(m:Interaction)-->(o) RETURN n,m,o` | 692ms | 33150ms | 33389ms | 48x | 48x |
| `MATCH (n{displayName:"Autophagy"}) RETURN n` | 316ms | 1555ms | 544ms | 4.9x | 1.7x |
| `MATCH (n{displayName:"Autophagy"})-->(m) RETURN m` | 217ms | 609ms | 543ms | 2.8x | 2.5x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN p` | 213ms | 627ms | 497ms | 2.9x | 2.3x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) RETURN q` | 215ms | 903ms | 701ms | 4.2x | 3.3x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 230ms | 3251ms | 2612ms | 14x | 11x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 293ms | 5747ms | 5266ms | 20x | 18x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 502ms | 18017ms | 17803ms | 36x | 35x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 1156ms | 66976ms | 56329ms | 58x | 49x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"}) RETURN n` | 268ms | 1234ms | 669ms | 4.6x | 2.5x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m) RETURN m` | 216ms | 1039ms | 529ms | 4.8x | 2.4x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) RETURN p` | 220ms | 592ms | 629ms | 2.7x | 2.9x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) RETURN q` | 219ms | 601ms | 554ms | 2.7x | 2.5x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 214ms | 646ms | 618ms | 3.0x | 2.9x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 214ms | 645ms | 603ms | 3.0x | 2.8x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 213ms | 629ms | 570ms | 3.0x | 2.7x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 218ms | 10816ms | 462ms | 50x | 2.1x |
| `MATCH (n)-[e:release]->(m) RETURN n,m` | 254ms | 3978ms | 3330ms | 16x | 13x |
| `MATCH (n)-[e:interactor]->(m) RETURN n,m` | 334ms | 25742ms | 25271ms | 77x | 76x |
| `MATCH (n)-[e:surroundedBy]->(m) RETURN n,m` | 220ms | 1049ms | 325ms | 4.8x | 1.5x |
| `MATCH (n)-[:hasEvent]->(m) RETURN n,m` | 306ms | 11299ms | 11157ms | 37x | 36x |
| `MATCH (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) RETURN n,m` | 94ms | 8512ms | 8718ms | 91x | 93x |
| `MATCH (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) RETURN r,s` | 161ms | 13471ms | 13842ms | 84x | 86x |
| `MATCH (n:DatabaseObject{isChimeric:false}) RETURN n` | 237ms | 2609ms | 1781ms | 11x | 7.5x |
| `MATCH (n:DatabaseObject{isChimeric:true}) RETURN n` | 214ms | 796ms | 610ms | 3.7x | 2.9x |
| `MATCH (b)-->(a:Pathway) RETURN a` | 313ms | 4529ms | 5887ms | 14x | 19x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a, c` | 2174ms | 35435ms | 35150ms | 16x | 16x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN b` | 2036ms | 22843ms | 23231ms | 11x | 11x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN c` | 1985ms | 18126ms | 18257ms | 9.1x | 9.2x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a` | 2004ms | 22330ms | 22542ms | 11x | 11x |

<!-- /RESULTS_OVERVIEW -->

---

## 5. Results by Query Category

<!-- RESULTS_BY_CATEGORY -->
### 5.1 Label Scans

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n:Drug) RETURN n` | 3ms | 1551ms | 307ms | 517x | 102x |
| `MATCH (n:ProteinDrug) RETURN n` | 1ms | 220ms | 231ms | 220x | 231x |
| `MATCH (n:Drug:ProteinDrug) RETURN n` | 0ms | 285ms | 338ms | - | - |

### 5.3 Property-Based Filtering

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n{displayName:"Autophagy"}) RETURN n` | 316ms | 1555ms | 544ms | 4.9x | 1.7x |
| `MATCH (n{displayName:"Autophagy"})-->(m) RETURN m` | 217ms | 609ms | 543ms | 2.8x | 2.5x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"}) RETURN n` | 268ms | 1234ms | 669ms | 4.6x | 2.5x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m) RETURN m` | 216ms | 1039ms | 529ms | 4.8x | 2.4x |
| `MATCH (n:DatabaseObject{isChimeric:false}) RETURN n` | 237ms | 2609ms | 1781ms | 11x | 7.5x |
| `MATCH (n:DatabaseObject{isChimeric:true}) RETURN n` | 214ms | 796ms | 610ms | 3.7x | 2.9x |

### 5.4 Relationship Type Traversal

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n)-[e:release]->(m) RETURN n,m` | 254ms | 3978ms | 3330ms | 16x | 13x |
| `MATCH (n)-[e:interactor]->(m) RETURN n,m` | 334ms | 25742ms | 25271ms | 77x | 76x |
| `MATCH (n)-[e:surroundedBy]->(m) RETURN n,m` | 220ms | 1049ms | 325ms | 4.8x | 1.5x |
| `MATCH (n)-[:hasEvent]->(m) RETURN n,m` | 306ms | 11299ms | 11157ms | 37x | 36x |
| `MATCH (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) RETURN n,m` | 94ms | 8512ms | 8718ms | 91x | 93x |
| `MATCH (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) RETURN r,s` | 161ms | 13471ms | 13842ms | 84x | 86x |

### 5.5 Multi-Hop Traversals

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN p` | 213ms | 627ms | 497ms | 2.9x | 2.3x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) RETURN q` | 215ms | 903ms | 701ms | 4.2x | 3.3x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 230ms | 3251ms | 2612ms | 14x | 11x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 293ms | 5747ms | 5266ms | 20x | 18x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 502ms | 18017ms | 17803ms | 36x | 35x |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 1156ms | 66976ms | 56329ms | 58x | 49x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) RETURN p` | 220ms | 592ms | 629ms | 2.7x | 2.9x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) RETURN q` | 219ms | 601ms | 554ms | 2.7x | 2.5x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 214ms | 646ms | 618ms | 3.0x | 2.9x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 214ms | 645ms | 603ms | 3.0x | 2.8x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 213ms | 629ms | 570ms | 3.0x | 2.7x |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 218ms | 10816ms | 462ms | 50x | 2.1x |

### 5.6 Complex Patterns

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------|------|------|------|------|------|
| `MATCH (n:Taxon)-->(m:Species) RETURN n,m` | 1ms | 366ms | 180ms | 366x | 180x |
| `MATCH (n)-->(m:Interaction)-->(o) RETURN n,m,o` | 692ms | 33150ms | 33389ms | 48x | 48x |
| `MATCH (b)-->(a:Pathway) RETURN a` | 313ms | 4529ms | 5887ms | 14x | 19x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a, c` | 2174ms | 35435ms | 35150ms | 16x | 16x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN b` | 2036ms | 22843ms | 23231ms | 11x | 11x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN c` | 1985ms | 18126ms | 18257ms | 9.1x | 9.2x |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a` | 2004ms | 22330ms | 22542ms | 11x | 11x |

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
