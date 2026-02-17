# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**turing-bench** is a graph database benchmarking tool that measures query performance across TuringDB, Neo4j, and Memgraph using real-world datasets.

## Commands

### Running benchmarks
```bash
# Full benchmark pipeline: stops all DBs, loads dataset, benchmarks all 3 engines,
# saves raw output to reports/, and updates the README summary table
./run.sh reactome                      # default dataset
./run.sh poledb queries_poledb.cypher  # specify dataset + query file
./run.sh --report reactome             # also generate full benchmark report (.md)
./run.sh --no-readme reactome          # skip README update

# Run individual benchmarks
uv run python -m turingbench turingdb --query-file sample_queries/reactome/queries_reactome.cypher --database=reactome
uv run python -m turingbench neo4j --query-file sample_queries/reactome/queries_reactome.cypher
uv run python -m turingbench memgraph --query-file sample_queries/reactome/queries_reactome.cypher --url=bolt://localhost:7688
```

### Server management
```bash
source env.sh  # required - sets up PATH, aliases, env vars
bench turingdb start -- -turing-dir dumps/reactome.turingdb -load reactome
bench neo4j start
bench memgraph start -- --data-directory=dumps/reactome.memgraph
bench <server> stop
bench all stop
```

### Report generation
```bash
# Parse raw benchmark output and update README with summary table
uv run python report_summary/parse_raw_benchmark.py <report_file> --dataset <name> --update-readme

# Other output formats
uv run python report_summary/parse_raw_benchmark.py <report_file> --dataset <name> --print --csv --markdown

# Generate full benchmark report from all raw benchmarks
uv run python report_summary/generate_benchmark_report.py --reports-dir reports/ -o reports/benchmark_report.md
```

### Linting and type checking
```bash
uv run ruff format .    # format code
uv run ruff check .     # lint
uv run ty check .       # type check
```

## Architecture

### Benchmarking framework (`turingbench/`)
- **`abstract_driver.py`** — `AbstractDriver` base class using Template Method pattern. Subclasses implement `execute_query()` and `close()`. The base handles timing (nanosecond precision via `perf_counter_ns`), multi-run execution, and result presentation (mean/min/max/median/throughput).
- **`neo4j_driver.py`** — Shared driver for both Neo4j (port 7687) and Memgraph (port 7688) since both speak the Bolt protocol.
- **`turingdb_driver.py`** — TuringDB driver using `turingdb` Python client against `http://localhost:6666`.
- **`__main__.py`** — CLI with three subcommands: `turingdb`, `neo4j`, `memgraph`.

### Raw benchmark parser (`report_summary/parse_raw_benchmark.py`)
`BenchmarkReportParser` parses raw benchmark output (`{dataset}_raw_benchmark.txt` — per-engine timing tables), extracts mean runtimes, computes TuringDB speedup ratios vs Neo4j and Memgraph, and can output as CSV, text, markdown, or directly update the README. Also collects machine specs (CPU, RAM, OS, storage) to include in each benchmark subsection. Called automatically by `run.sh` at the end of a benchmark run.

### Benchmark report generator (`report_summary/generate_benchmark_report.py`)
`ReportGenerator` combines all raw benchmark results into a comprehensive markdown report using `BENCHMARK_REPORT_TEMPLATE.md`. Auto-populates dataset statistics from JSONL files, hardware/software info, results tables, executive summary, and query appendix. Invoked via `run.sh --report` or standalone.

### Server orchestration (`scripts/manage_servers.py`)
`ServerManager` handles process lifecycle with PID file tracking in `scripts/.cache/`. Each database has a different health check strategy: Neo4j uses process grep, Memgraph uses `mgconsole` test query, TuringDB uses Python client warmup. Aliased as `bench` via `env.sh`.

### Key environment setup (`env.sh`)
All paths and aliases are defined here. Must be sourced before running any scripts. Databases are installed under `install/`, datasets stored under `dumps/`.

## DBMS Install process

- Run `install.sh` to install Neo4j and Memgraph (under `install/`)
- TuringDB is a Python dependency, installed automatically via `uv` when running benchmarks

## Dataset import

Datasets are downloaded and converted into all three engine formats using:
```bash
./scripts/neo4j-43-imports/run_all.sh <dataset>  # e.g. reactome, poledb
```

This pipeline downloads the raw Neo4j 4.3 dump, migrates it to Neo4j 5, exports to Cypher and JSONL, then loads into Memgraph and TuringDB.

## Dependencies

- Python ≥ 3.13, managed with `uv`
- Dev tools: `ruff` (formatter/linter), `ty` (type checker)

## Dataset conventions

Each dataset `$NAME` produces files under `dumps/`:
- `$NAME.neo4j/` — Neo4j database directory
- `$NAME.memgraph/` — Memgraph snapshot
- `$NAME.turingdb/` — TuringDB format
- `$NAME.cypher` — Full Cypher script (schema + data)
- `$NAME.jsonl` — JSON Lines export

Query files live in `sample_queries/$NAME/`.
