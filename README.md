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
| Query | TuringDB | Neo4j | Memgraph |
|------------------------------------------------------------------------------------------------------------------|----------|--------|----------|
| MATCH (n) RETURN n                                                                                               | 73ms     | 3635ms | 2480ms   |
| MATCH (p:Person) RETURN p                                                                                        | 5ms      | 151ms  | 28ms     |
| MATCH (p:Person) RETURN count(p)                                                                                 | 1ms      | 110ms  | 9ms      |
| MATCH (c:Crime) RETURN c                                                                                         | 30ms     | 1411ms | 1308ms   |
| MATCH (c:Crime) RETURN count(c)                                                                                  | 2ms      | 41ms   | 14ms     |
| MATCH ()-[r]->() RETURN r                                                                                        | 120ms    | 4546ms | 4088ms   |
| MATCH ()-[r]->() RETURN count(r)                                                                                 | 11ms     | 78ms   | 29ms     |
| MATCH (p:Person {name: 'John'})-[:PARTY_TO]->(c:Crime) RETURN p, c                                               | 4ms      | 185ms  | 4ms      |
| MATCH (p:Person)-[:PARTY_TO]->(c:Crime) RETURN p.name, p.surname, c.type                                         | 1ms      | 86ms   | 12ms     |
| MATCH (p:Person {surname: 'Smith'})-[r]->(n) RETURN p                                                            | 3ms      | 48ms   | 2ms      |
| MATCH (p:Person)-[r]->(n) WHERE p.surname = 'Smith' RETURN p                                                     | 3ms      | 43ms   | 1ms      |
| MATCH (p1:Person)-[:PARTY_TO]->(c:Crime)<-[:PARTY_TO]-(p2:Person) WHERE p1 <> p2 RETURN p1.name, p2.name, c.type | 1ms      | 97ms   | 10ms     |
| MATCH (p1:Person)-[:KNOWS]->(p2:Person)-[:PARTY_TO]->(c:Crime) RETURN p1.name, p2.name                           | 1ms      | 59ms   | 11ms     |
| MATCH (c:Crime)-[:OCCURRED_AT]->(l:Location) RETURN l.postcode                                                   | 46ms     | 706ms  | 557ms    |
| MATCH (p1)-[:PARTY_TO]->(c:Crime), (p2)-[:PARTY_TO]->(c:Crime) RETURN p1.name, p2.name, c.type                   | 21ms     | 105ms  | 12ms     |
<!-- BENCHMARK_RESULTS_POLEDB_END -->

### Reactome

<!-- BENCHMARK_RESULTS_REACTOME_START -->
| Query | TuringDB | Memgraph | Neo4j |
|-----------------------------------------------------------------------------------------------------------|----------|----------|----------|
| match (n:Drug) return n                                                                                   | 5ms      | 404ms    | 1872ms   |
| match (n:ProteinDrug) return n                                                                            | 2ms      | 356ms    | 420ms    |
| match (n:Drug:ProteinDrug) return n                                                                       | 1ms      | 339ms    | 568ms    |
| match (n:Taxon)-->(m:Species) return n,m                                                                  | 2ms      | 333ms    | 555ms    |
| match (n)-->(m:Interaction)-->(o) return n,m,o                                                            | 1265ms   | 343ms    | 74769ms  |
| match (n{displayName:"Autophagy"}) return n                                                               | 275ms    | 927ms    | 1497ms   |
| match (n{displayName:"Autophagy"})-->(m) return m                                                         | 237ms    | 942ms    | 1351ms   |
| match (n{displayName:"Autophagy"})-->(m)-->(p) return p                                                   | 238ms    | 1029ms   | 1351ms   |
| match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q) return q                                             | 252ms    | 1470ms   | 3845ms   |
| match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r) return r                                       | 297ms    | 3626ms   | 4170ms   |
| match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s) return s                                 | 469ms    | 11537ms  | 12438ms  |
| match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) return t                           | 1085ms   | 36782ms  | 41730ms  |
| match (n{displayName:"Autophagy"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) return v                     | 3002ms   | 104928ms | 153377ms |
| match (n{displayName:"APOE-4 [extracellular region]"}) return n                                           | 401ms    | 1271ms   | 1631ms   |
| match (n{displayName:"APOE-4 [extracellular region]"})-->(m) return m                                     | 238ms    | 965ms    | 1370ms   |
| match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p) return p                               | 244ms    | 979ms    | 1337ms   |
| match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q) return q                         | 251ms    | 1034ms   | 1342ms   |
| match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r) return r                   | 242ms    | 969ms    | 1449ms   |
| match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s) return s             | 250ms    | 971ms    | 1422ms   |
| match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t) return t       | 245ms    | 1044ms   | 1472ms   |
| match (n{displayName:"APOE-4 [extracellular region]"})-->(m)-->(p)-->(q)-->(r)-->(s)-->(t)-->(v) return v | 249ms    | 966ms    | 21038ms  |
| match (n)-[e:release]->(m) return n,m                                                                     | 487ms    | 363ms    | 9390ms   |
| match (n)-[e:interactor]->(m) return n,m                                                                  | 759ms    | 374ms    | 58195ms  |
| match (n)-[e:surroundedBy]->(m) return n,m                                                                | 329ms    | 389ms    | 2068ms   |
| match (n)-[:hasEvent]->(m) return n,m                                                                     | 620ms    | 16511ms  | 25504ms  |
| match (n:Pathway)-[:hasEvent]->(m:ReactionLikeEvent) return n,m                                           | 257ms    | 13822ms  | 19495ms  |
| match (r:ReactionLikeEvent)-[:output]->(s:PhysicalEntity) return r,s                                      | 424ms    | 24931ms  | 31566ms  |
| match (n:DatabaseObject{isChimeric:false}) return n                                                       | 757ms    | 3521ms   | 5782ms   |
| match (n:DatabaseObject{isChimeric:true}) return n                                                        | 627ms    | 960ms    | 1847ms   |
| match (b)-->(a:Pathway) return a                                                                          | 735ms    | 8779ms   | 12998ms  |
| match (c)-->(b)-->(a:Pathway) return a, c                                                                 | 5354ms   | 39263ms  | 79518ms  |
| match (c)-->(b)-->(a:Pathway) return b                                                                    | 4927ms   | 25646ms  | 53988ms  |
| match (c)-->(b)-->(a:Pathway) return c                                                                    | 4913ms   | 21601ms  | 42944ms  |
| match (c)-->(b)-->(a:Pathway) return a                                                                    | 4761ms   | 26180ms  | 54560ms  |
<!-- BENCHMARK_RESULTS_REACTOME_END -->


