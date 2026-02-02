#!/usr/bin/env bash

set -e
shopt -s expand_aliases

GIT_ROOT="$(git rev-parse --show-toplevel)"

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$script_dir/servers_python"
alias uvrun="uv run --directory $GIT_ROOT python -m turingbench"

uv run python manage_servers.py turingdb stop > /dev/null || true
uv run python manage_servers.py neo4j stop > /dev/null || true
uv run python manage_servers.py memgraph stop > /dev/null || true

# TuringDB benchmark
uv run python manage_servers.py turingdb start || true
uvrun turingdb --query-file '/home/dev/work/turing-bench/sample_queries/simpledb/labelsets.cypher'
uv run python manage_servers.py turingdb stop

# Neo4j benchmark
uv run python manage_servers.py neo4j start
uvrun neo4j --query-file '/home/dev/work/turing-bench/sample_queries/simpledb/labelsets.cypher'
uv run python manage_servers.py neo4j stop

# Memgraph benchmark
uv run python manage_servers.py memgraph start
uvrun memgraph --query-file '/home/dev/work/turing-bench/sample_queries/simpledb/labelsets.cypher' --database=memgraph
uv run python manage_servers.py memgraph stop
