# TuringDB Benchmark Report

> **Date:** 2026-03-24
> **Author(s):** TuringDB team

## Executive Summary

TuringDB is a column-oriented, in-memory graph database engine designed for analytical and read-intensive workloads. This report presents benchmark results comparing TuringDB against Neo4j and Memgraph across multiple datasets and query categories.

**Key findings:**

<!-- EXECUTIVE_SUMMARY -->
- Across **1 dataset(s)** and **34 queries**:
- TuringDB is **52.3x faster** than Neo4j on average (median 14.0x, max 294x)
- TuringDB wins on **33/33** queries vs Neo4j
- TuringDB is **38.6x faster** than Memgraph on average (median 12.0x, max 303x)
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
| turingdb (Python SDK)  | 1.24.0                  |
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

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph | Δ TuringDB |
|-------|------|------|------|------|------|--------|
| `MATCH (n:Drug) RETURN n` | 4ms | 1081ms | 262ms | 270x | 66x | +33.3% |
| `MATCH (n:ProteinDrug) RETURN n` | 1ms | 224ms | 200ms | 224x | 200x | +0.0% |
| `MATCH (n:Drug:ProteinDrug) RETURN n` | 0ms | 287ms | 276ms | - | - | - |
| `MATCH (n:Taxon)-->(m:Species) RETURN n,m` | 1ms | 294ms | 303ms | 294x | 303x | +0.0% |
| `MATCH (n)-->(m:Interaction)-->(o) RETURN n,m,o` | 677ms | 33189ms | 32706ms | 49x | 48x | +2.1% |
| `MATCH (n{displayName:"Autophagy"}) RETURN n` | 95ms | 1164ms | 526ms | 12x | 5.5x | -4.0% |
| `MATCH (n{displayName:"Autophagy"})-->(m) RETURN m` | 64ms | 841ms | 546ms | 13x | 8.5x | -28.1% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN p` | 60ms | 613ms | 447ms | 10x | 7.5x | -36.2% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) RETURN q` | 63ms | 891ms | 791ms | 14x | 13x | -36.4% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 78ms | 2764ms | 2658ms | 35x | 34x | -7.1% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 142ms | 5895ms | 5200ms | 42x | 37x | -22.0% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 357ms | 18412ms | 17421ms | 52x | 49x | -14.2% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 1017ms | 68098ms | 55046ms | 67x | 54x | -8.3% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"}) RETURN n` | 159ms | 731ms | 517ms | 4.6x | 3.3x | +9.7% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m) RETURN m` | 55ms | 612ms | 632ms | 11x | 11x | -39.6% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) RETURN p` | 60ms | 601ms | 614ms | 10x | 10x | -35.5% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) RETURN q` | 61ms | 608ms | 539ms | 10.0x | 8.8x | -25.6% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 62ms | 628ms | 604ms | 10x | 9.7x | -31.9% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 59ms | 628ms | 454ms | 11x | 7.7x | -36.6% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 60ms | 643ms | 468ms | 11x | 7.8x | -36.2% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 60ms | 11181ms | 568ms | 186x | 9.5x | -38.1% |
| `MATCH (n)-[e:release]->(m) RETURN n,m` | 249ms | 3967ms | 3170ms | 16x | 13x | +0.4% |
| `MATCH (n)-[e:interactor]->(m) RETURN n,m` | 327ms | 25723ms | 25218ms | 79x | 77x | -1.5% |
| `MATCH (n)-[e:surroundedBy]->(m) RETURN n,m` | 296ms | 1108ms | 359ms | 3.7x | 1.2x | +37.0% |
| `MATCH (n)-[:hasEvent]->(m) RETURN n,m` | 284ms | 11269ms | 11124ms | 40x | 39x | -6.6% |
| `MATCH (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) RETURN n,m` | 97ms | 8578ms | 8851ms | 88x | 91x | +1.0% |
| `MATCH (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) RETURN r,s` | 166ms | 13564ms | 13567ms | 82x | 82x | -10.8% |
| `MATCH (n:DatabaseObject{isChimeric:false}) RETURN n` | 279ms | 2972ms | 1678ms | 11x | 6.0x | +7.7% |
| `MATCH (n:DatabaseObject{isChimeric:true}) RETURN n` | 359ms | 1364ms | 434ms | 3.8x | 1.2x | +45.3% |
| `MATCH (b)-->(a:Pathway) RETURN a` | 300ms | 4506ms | 5912ms | 15x | 20x | -4.2% |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a, c` | 2102ms | 35548ms | 34344ms | 17x | 16x | -2.4% |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN b` | 1925ms | 22886ms | 22953ms | 12x | 12x | -6.4% |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN c` | 1935ms | 18299ms | 17962ms | 9.5x | 9.3x | -2.2% |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a` | 1930ms | 22401ms | 22334ms | 12x | 12x | -6.4% |

<!-- /RESULTS_OVERVIEW -->

---

## 5. Results by Query Category

<!-- RESULTS_BY_CATEGORY -->
### 5.1 Label Scans

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph | Δ TuringDB |
|-------|------|------|------|------|------|--------|
| `MATCH (n:Drug) RETURN n` | 4ms | 1081ms | 262ms | 270x | 66x | +33.3% |
| `MATCH (n:ProteinDrug) RETURN n` | 1ms | 224ms | 200ms | 224x | 200x | +0.0% |
| `MATCH (n:Drug:ProteinDrug) RETURN n` | 0ms | 287ms | 276ms | - | - | - |

### 5.3 Property-Based Filtering

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph | Δ TuringDB |
|-------|------|------|------|------|------|--------|
| `MATCH (n{displayName:"Autophagy"}) RETURN n` | 95ms | 1164ms | 526ms | 12x | 5.5x | -4.0% |
| `MATCH (n{displayName:"Autophagy"})-->(m) RETURN m` | 64ms | 841ms | 546ms | 13x | 8.5x | -28.1% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"}) RETURN n` | 159ms | 731ms | 517ms | 4.6x | 3.3x | +9.7% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m) RETURN m` | 55ms | 612ms | 632ms | 11x | 11x | -39.6% |
| `MATCH (n:DatabaseObject{isChimeric:false}) RETURN n` | 279ms | 2972ms | 1678ms | 11x | 6.0x | +7.7% |
| `MATCH (n:DatabaseObject{isChimeric:true}) RETURN n` | 359ms | 1364ms | 434ms | 3.8x | 1.2x | +45.3% |

### 5.4 Relationship Type Traversal

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph | Δ TuringDB |
|-------|------|------|------|------|------|--------|
| `MATCH (n)-[e:release]->(m) RETURN n,m` | 249ms | 3967ms | 3170ms | 16x | 13x | +0.4% |
| `MATCH (n)-[e:interactor]->(m) RETURN n,m` | 327ms | 25723ms | 25218ms | 79x | 77x | -1.5% |
| `MATCH (n)-[e:surroundedBy]->(m) RETURN n,m` | 296ms | 1108ms | 359ms | 3.7x | 1.2x | +37.0% |
| `MATCH (n)-[:hasEvent]->(m) RETURN n,m` | 284ms | 11269ms | 11124ms | 40x | 39x | -6.6% |
| `MATCH (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) RETURN n,m` | 97ms | 8578ms | 8851ms | 88x | 91x | +1.0% |
| `MATCH (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) RETURN r,s` | 166ms | 13564ms | 13567ms | 82x | 82x | -10.8% |

### 5.5 Multi-Hop Traversals

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph | Δ TuringDB |
|-------|------|------|------|------|------|--------|
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p) RETURN p` | 60ms | 613ms | 447ms | 10x | 7.5x | -36.2% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) RETURN q` | 63ms | 891ms | 791ms | 14x | 13x | -36.4% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 78ms | 2764ms | 2658ms | 35x | 34x | -7.1% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 142ms | 5895ms | 5200ms | 42x | 37x | -22.0% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 357ms | 18412ms | 17421ms | 52x | 49x | -14.2% |
| `MATCH (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 1017ms | 68098ms | 55046ms | 67x | 54x | -8.3% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) RETURN p` | 60ms | 601ms | 614ms | 10x | 10x | -35.5% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) RETURN q` | 61ms | 608ms | 539ms | 10.0x | 8.8x | -25.6% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) RETURN r` | 62ms | 628ms | 604ms | 10x | 9.7x | -31.9% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) RETURN s` | 59ms | 628ms | 454ms | 11x | 7.7x | -36.6% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) RETURN t` | 60ms | 643ms | 468ms | 11x | 7.8x | -36.2% |
| `MATCH (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) RETURN v` | 60ms | 11181ms | 568ms | 186x | 9.5x | -38.1% |

### 5.6 Complex Patterns

**Reactome:**

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph | Δ TuringDB |
|-------|------|------|------|------|------|--------|
| `MATCH (n:Taxon)-->(m:Species) RETURN n,m` | 1ms | 294ms | 303ms | 294x | 303x | +0.0% |
| `MATCH (n)-->(m:Interaction)-->(o) RETURN n,m,o` | 677ms | 33189ms | 32706ms | 49x | 48x | +2.1% |
| `MATCH (b)-->(a:Pathway) RETURN a` | 300ms | 4506ms | 5912ms | 15x | 20x | -4.2% |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a, c` | 2102ms | 35548ms | 34344ms | 17x | 16x | -2.4% |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN b` | 1925ms | 22886ms | 22953ms | 12x | 12x | -6.4% |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN c` | 1935ms | 18299ms | 17962ms | 9.5x | 9.3x | -2.2% |
| `MATCH (c)-->(b)-->(a:Pathway) RETURN a` | 1930ms | 22401ms | 22334ms | 12x | 12x | -6.4% |

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