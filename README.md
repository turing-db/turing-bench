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

