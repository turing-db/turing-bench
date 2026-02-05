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


