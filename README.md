# `turing-bench`
> Benchmarking tool for TuringDB.

## Usage (TuringDB)
1. Run a TuringDB instance, noting the address where the instance can be hit
2. Run the `turingdb_driver.py` script,

Example usage:

```bash
python3 turingdb_driver.py --query turingdbsample.cypher --database reactome --url 'http://localhost:6666' --runs 100
```

This will run the queries in `turingdbsample.cypher` against the `reactome` database, running each query `100` times.

You may specify any URL and port with a running TuringDB server using the `--url` or `-u` options. If left unspecified, `turing-bench` assumes there is a TuringDB server running locally, and attempts to query `http://127.0.0.1:6666`.

## Usage (Other DBs)
Other DBs can be supported by inheriting from and implementing the `AbstractDriver` class (see `drivers/neo4j_driver.py` or `drivers/turingdb_driver.py` for examples).

## Installation of other DBMSs: Neo4j and Memgraph

> [!WARNING]
> The script can only be ran on Debian based systems for now.

Run the `./install.sh` script to install the necessary dependencies as well as Neo4j and Memgraph.

> [!NOTE]
> Optionnaly, run `./install.sh --clean` to run a clean install 

- Run `source ./env.sh` to setup the environment variables


## Benchmark Results
### Poledb

<!-- BENCHMARK_RESULTS_POLEDB_START -->
| Query | TuringDB | Neo4j | Memgraph |
|--------------------------------------------------------------------------------|--------------------|--------------------|--------------------|
| MATCH (n) RETURN n | 73ms | 3635ms | 2480ms |
| MATCH (p:Person) RETURN p | 5ms | 151ms | 28ms |
| MATCH (p:Person) RETURN count(p) | 1ms | 110ms | 9ms |
| MATCH (c:Crime) RETURN c | 30ms | 1411ms | 1308ms |
| MATCH (c:Crime) RETURN count(c) | 2ms | 41ms | 14ms |
| MATCH ()-[r]->() RETURN r | 120ms | 4546ms | 4088ms |
| MATCH ()-[r]->() RETURN count(r) | 11ms | 78ms | 29ms |
| MATCH (p:Person {name: 'John'})-[:PARTY_TO]->(c:Crime) RETURN p, c | 4ms | 185ms | 4ms |
| MATCH (p:Person)-[:PARTY_TO]->(c:Crime) RETURN p.name, p.surname, c.type | 1ms | 86ms | 12ms |
| MATCH (p:Person {surname: 'Smith'})-[r]->(n) RETURN p | 3ms | 48ms | 2ms |
| MATCH (p:Person)-[r]->(n) WHERE p.surname = 'Smith' RETURN p | 3ms | 43ms | 1ms |
| MATCH (p1:Person)-[:PARTY_TO]->(c:Crime)<-[:PARTY_TO]-(p2:Person) WHERE p1 <> p2 RETURN p1.name, p2.name, c.type | 1ms | 97ms | 10ms |
| MATCH (p1:Person)-[:KNOWS]->(p2:Person)-[:PARTY_TO]->(c:Crime) RETURN p1.name, p2.name | 1ms | 59ms | 11ms |
| MATCH (c:Crime)-[:OCCURRED_AT]->(l:Location) RETURN l.postcode | 46ms | 706ms | 557ms |
| MATCH (p1)-[:PARTY_TO]->(c:Crime), (p2)-[:PARTY_TO]->(c:Crime) RETURN p1.name, p2.name, c.type | 21ms | 105ms | 12ms |
<!-- BENCHMARK_RESULTS_POLEDB_END -->


