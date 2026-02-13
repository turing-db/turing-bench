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
| `MATCH (n) RETURN n`                                                                                               | 91ms     | 3692ms | 2495ms   | 41x              | 27x                 |
| `MATCH (p:Person) RETURN p`                                                                                        | 5ms      | 141ms  | 32ms     | 28x              | 6.4x                |
| `MATCH (p:Person) RETURN count(p)`                                                                                 | 1ms      | 95ms   | 11ms     | 95x              | 11x                 |
| `MATCH (c:Crime) RETURN c`                                                                                         | 30ms     | 1396ms | 1305ms   | 47x              | 44x                 |
| `MATCH (c:Crime) RETURN count(c)`                                                                                  | 2ms      | 68ms   | 13ms     | 34x              | 6.5x                |
| `MATCH ()-[r]->() RETURN r`                                                                                        | 120ms    | 4520ms | 4133ms   | 38x              | 34x                 |
| `MATCH ()-[r]->() RETURN count(r)`                                                                                 | 11ms     | 81ms   | 49ms     | 7.4x             | 4.5x                |
| `MATCH (p:Person {name: 'John'})-[:PARTY_TO]->(c:Crime) RETURN p, c`                                               | 3ms      | 16ms   | 1ms      | 5.3x             | 0.3x                |
| `MATCH (p:Person)-[:PARTY_TO]->(c:Crime) RETURN p.name, p.surname, c.type`                                         | 1ms      | 19ms   | 11ms     | 19x              | 11x                 |
| `MATCH (p:Person {surname: 'Smith'})-[r]->(n) RETURN p`                                                            | 4ms      | 42ms   | 1ms      | 10x              | 0.2x                |
| `MATCH (p:Person)-[r]->(n) WHERE p.surname = 'Smith' RETURN p`                                                     | 4ms      | 38ms   | 1ms      | 9.5x             | 0.2x                |
| `MATCH (p1:Person)-[:PARTY_TO]->(c:Crime)<-[:PARTY_TO]-(p2:Person) WHERE p1 <> p2 RETURN p1.name, p2.name, c.type` | 1ms      | 90ms   | 8ms      | 90x              | 8.0x                |
| `MATCH (p1:Person)-[:KNOWS]->(p2:Person)-[:PARTY_TO]->(c:Crime) RETURN p1.name, p2.name`                           | 1ms      | 20ms   | 13ms     | 20x              | 13x                 |
| `MATCH (c:Crime)-[:OCCURRED_AT]->(l:Location) RETURN l.postcode`                                                   | 48ms     | 744ms  | 573ms    | 16x              | 12x                 |
<!-- BENCHMARK_RESULTS_POLEDB_END -->
