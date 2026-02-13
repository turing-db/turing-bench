# `turing-bench`

Graph database benchmarking tool that measures query performance across **TuringDB**, **Neo4j**, and **Memgraph** using real-world datasets (Reactome, PoleDB).

## Prerequisites

- Linux (Debian-based, e.g. Ubuntu 22.04)
- Python >= 3.13
- [`uv`](https://docs.astral.sh/uv/) (Python package manager)
- `wget`, `git`, `tar`, `dpkg-deb`
- AWS CLI configured with the `turingdb_intern` profile (for downloading datasets)

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/turing-db/turing-bench.git
cd turing-bench
```

### 2. Install database engines

> [!WARNING]
> The install script only supports Debian-based systems. It downloads and builds Neo4j from source, which requires Java 17 and Maven (both installed automatically).

```bash
./install.sh
# To start fresh, run: ./install.sh --clean
```

This installs the following under `install/`:
- **Java 17** and **Maven** (needed to build Neo4j)
- **Neo4j** (community edition, built from source) + APOC plugin
- **Memgraph** (extracted from `.deb` package)

TuringDB is installed automatically as a Python dependency when running the benchmark.

### 3. Set up the environment

This must be run in every new shell session before using `bench` or running benchmarks:

```bash
source env.sh
```

This adds database binaries to your `PATH` and defines the `bench` alias used to manage servers.

### 4. Download and import datasets

Each dataset must be downloaded and converted into the formats used by all three engines. The `run_all.sh` script handles the full pipeline:

```bash
./scripts/neo4j-43-imports/run_all.sh reactome
./scripts/neo4j-43-imports/run_all.sh poledb
```

For each dataset, this runs the following steps (see `scripts/neo4j-43-imports/`):

1. **Download** the raw Neo4j 4.3 dump (`0_download.sh`)
2. **Migrate** the dump to Neo4j 5 and save it to `dumps/<dataset>.neo4j` (`1_migrate.sh`)
3. **Export to Cypher** -- generates a `.cypher` script containing all nodes, relationships, and indexes. This script will be used to generate Memgraph dump. (`2_gen_cypher.sh`)
4. **Export to JSONL** -- generates a `.jsonl` file with the dataset in JSON Lines format. This graph will be used to create TuringDB graph. (`3_gen_jsonl.sh`)
5. **Load into Memgraph** and save snapshot to `dumps/<dataset>.memgraph` (`4_load_in_memgraph.sh`)
6. **Load into TuringDB** and save to `dumps/<dataset>.turingdb` (`5_load_in_turingdb.sh`)

> [!NOTE]
> All three database engines must be installed (step 2) before importing datasets, since the pipeline starts and stops each engine during the process.

## Running benchmarks

### Full benchmark (all three engines)

The `run.sh` script stops all databases, loads the specified dataset, and benchmarks each engine sequentially:

```bash
./run.sh reactome                       # uses default query file
./run.sh poledb queries_poledb.cypher   # specify dataset + query file
```

### Individual engine benchmarks

Start a database, run the benchmark, then stop it:

```bash
source env.sh

# TuringDB
bench turingdb start -- -turing-dir dumps/reactome.turingdb -load reactome
uv run python -m turingbench turingdb --query-file sample_queries/reactome/queries_reactome.cypher --database=reactome
bench turingdb stop

# Neo4j
bench neo4j start
uv run python -m turingbench neo4j --query-file sample_queries/reactome/queries_reactome.cypher
bench neo4j stop

# Memgraph
bench memgraph start -- --data-directory=dumps/reactome.memgraph
uv run python -m turingbench memgraph --query-file sample_queries/reactome/queries_reactome.cypher --url=bolt://localhost:7688
bench memgraph stop
```

### Server management

```bash
bench <engine> start    # start a database (turingdb, neo4j, memgraph)
bench <engine> stop     # stop a database
bench all stop          # stop all databases
```

## Available datasets

| Dataset    | Query file                                          |
|------------|-----------------------------------------------------|
| `reactome` | `sample_queries/reactome/queries_reactome.cypher`   |
| `poledb`   | `sample_queries/poledb/queries_poledb.cypher`       |

## Benchmark Results
### Poledb

<!-- BENCHMARK_RESULTS_POLEDB_START -->
> **CPU**: AMD EPYC 7313P 16-Core Processor | **Cores**: 32 | **RAM**: 125.4 GB | **OS**: Ubuntu 22.04.5 LTS | **Storage**: SSD

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|--------------------------------------------------------------------------------------------------------------------|----------|--------|----------|------------------|---------------------|
| `MATCH (n) RETURN n`                                                                                               | 89ms     | 3794ms | 2510ms   | 43x              | 28x                 |
| `MATCH (p:Person) RETURN p`                                                                                        | 5ms      | 148ms  | 36ms     | 30x              | 7.2x                |
| `MATCH (p:Person) RETURN count(p)`                                                                                 | 1ms      | 94ms   | 14ms     | 94x              | 14x                 |
| `MATCH (c:Crime) RETURN c`                                                                                         | 30ms     | 1414ms | 1311ms   | 47x              | 44x                 |
| `MATCH (c:Crime) RETURN count(c)`                                                                                  | 2ms      | 66ms   | 17ms     | 33x              | 8.5x                |
| `MATCH ()-[r]->() RETURN r`                                                                                        | 121ms    | 4596ms | 4174ms   | 38x              | 34x                 |
| `MATCH ()-[r]->() RETURN count(r)`                                                                                 | 11ms     | 80ms   | 50ms     | 7.3x             | 4.5x                |
| `MATCH (p:Person {name: 'John'})-[:PARTY_TO]->(c:Crime) RETURN p, c`                                               | 4ms      | 17ms   | 0ms      | 4.2x             | -                   |
| `MATCH (p:Person)-[:PARTY_TO]->(c:Crime) RETURN p.name, p.surname, c.type`                                         | 1ms      | 20ms   | 9ms      | 20x              | 9.0x                |
| `MATCH (p:Person {surname: 'Smith'})-[r]->(n) RETURN p`                                                            | 4ms      | 46ms   | 2ms      | 12x              | 0.5x                |
| `MATCH (p:Person)-[r]->(n) WHERE p.surname = 'Smith' RETURN p`                                                     | 4ms      | 41ms   | 1ms      | 10x              | 0.2x                |
| `MATCH (p1:Person)-[:PARTY_TO]->(c:Crime)<-[:PARTY_TO]-(p2:Person) WHERE p1 <> p2 RETURN p1.name, p2.name, c.type` | 1ms      | 90ms   | 8ms      | 90x              | 8.0x                |
| `MATCH (p1:Person)-[:KNOWS]->(p2:Person)-[:PARTY_TO]->(c:Crime) RETURN p1.name, p2.name`                           | 1ms      | 21ms   | 11ms     | 21x              | 11x                 |
| `MATCH (c:Crime)-[:OCCURRED_AT]->(l:Location) RETURN l.postcode`                                                   | 50ms     | 751ms  | 568ms    | 15x              | 11x                 |
<!-- BENCHMARK_RESULTS_POLEDB_END -->
### Reactome

<!-- BENCHMARK_RESULTS_REACTOME_START -->
> **CPU**: AMD EPYC 7313P 16-Core Processor | **Cores**: 32 | **RAM**: 125.4 GB | **OS**: Ubuntu 22.04.5 LTS | **Storage**: SSD

| Query | TuringDB | Neo4j | Memgraph | Speedup vs Neo4j | Speedup vs Memgraph |
|-------------------------------------------------------------------------------------------------------------|----------|----------|----------|------------------|---------------------|
| `match (n:Drug) return n`                                                                                   | 5ms      | 1872ms   | 404ms    | 374x             | 81x                 |
| `match (n:ProteinDrug) return n`                                                                            | 2ms      | 420ms    | 356ms    | 210x             | 178x                |
| `match (n:Drug:ProteinDrug) return n`                                                                       | 1ms      | 568ms    | 339ms    | 568x             | 339x                |
| `match (n:Taxon)-->(m:Species) return n,m`                                                                  | 2ms      | 555ms    | 333ms    | 278x             | 166x                |
| `match (n)-->(m:Interaction)-->(o) return n,m,o`                                                            | 1265ms   | 74769ms  | 343ms    | 59x              | 0.3x                |
| `match (n{displayName:"Autophagy"}) return n`                                                               | 275ms    | 1497ms   | 927ms    | 5.4x             | 3.4x                |
| `match (n{displayName:"Autophagy"})-->(m) return m`                                                         | 237ms    | 1351ms   | 942ms    | 5.7x             | 4.0x                |
| `match (n{displayName:"Autophagy"})-->(m)-->(p) return p`                                                   | 238ms    | 1351ms   | 1029ms   | 5.7x             | 4.3x                |
| `match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) return q`                                             | 252ms    | 3845ms   | 1470ms   | 15x              | 5.8x                |
| `match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) return r`                                       | 297ms    | 4170ms   | 3626ms   | 14x              | 12x                 |
| `match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) return s`                                 | 469ms    | 12438ms  | 11537ms  | 27x              | 25x                 |
| `match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) return t`                           | 1085ms   | 41730ms  | 36782ms  | 38x              | 34x                 |
| `match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) return v`                     | 3002ms   | 153377ms | 104928ms | 51x              | 35x                 |
| `match (n{displayName:"APOE-4 [extracellular region]"}) return n`                                           | 401ms    | 1631ms   | 1271ms   | 4.1x             | 3.2x                |
| `match (n{displayName:"APOE-4 [extracellular region]"})-->(m) return m`                                     | 238ms    | 1370ms   | 965ms    | 5.8x             | 4.1x                |
| `match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) return p`                               | 244ms    | 1337ms   | 979ms    | 5.5x             | 4.0x                |
| `match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) return q`                         | 251ms    | 1342ms   | 1034ms   | 5.3x             | 4.1x                |
| `match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) return r`                   | 242ms    | 1449ms   | 969ms    | 6.0x             | 4.0x                |
| `match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) return s`             | 250ms    | 1422ms   | 971ms    | 5.7x             | 3.9x                |
| `match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) return t`       | 245ms    | 1472ms   | 1044ms   | 6.0x             | 4.3x                |
| `match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) return v` | 249ms    | 21038ms  | 966ms    | 84x              | 3.9x                |
| `match (n)-[e:release]->(m) return n,m`                                                                     | 487ms    | 9390ms   | 363ms    | 19x              | 0.7x                |
| `match (n)-[e:interactor]->(m) return n,m`                                                                  | 759ms    | 58195ms  | 374ms    | 77x              | 0.5x                |
| `match (n)-[e:surroundedBy]->(m) return n,m`                                                                | 329ms    | 2068ms   | 389ms    | 6.3x             | 1.2x                |
| `match (n)-[:hasEvent]->(m) return n,m`                                                                     | 620ms    | 25504ms  | 16511ms  | 41x              | 27x                 |
| `match (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) return n,m`                                           | 257ms    | 19495ms  | 13822ms  | 76x              | 54x                 |
| `match (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) return r,s`                                      | 424ms    | 31566ms  | 24931ms  | 74x              | 59x                 |
| `match (n:DatabaseObject{isChimeric:false}) return n`                                                       | 757ms    | 5782ms   | 3521ms   | 7.6x             | 4.7x                |
| `match (n:DatabaseObject{isChimeric:true}) return n`                                                        | 627ms    | 1847ms   | 960ms    | 2.9x             | 1.5x                |
| `match (b)-->(a:Pathway) return a`                                                                          | 735ms    | 12998ms  | 8779ms   | 18x              | 12x                 |
| `match (c)-->(b)-->(a:Pathway) return a, c`                                                                 | 5354ms   | 79518ms  | 39263ms  | 15x              | 7.3x                |
| `match (c)-->(b)-->(a:Pathway) return b`                                                                    | 4927ms   | 53988ms  | 25646ms  | 11x              | 5.2x                |
| `match (c)-->(b)-->(a:Pathway) return c`                                                                    | 4913ms   | 42944ms  | 21601ms  | 8.7x             | 4.4x                |
| `match (c)-->(b)-->(a:Pathway) return a`                                                                    | 4761ms   | 54560ms  | 26180ms  | 11x              | 5.5x                |
<!-- BENCHMARK_RESULTS_REACTOME_END -->
