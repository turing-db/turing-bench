#!/usr/bin/env bash

# TuringDB benchmark
uv run python manage_servers.py turingdb start
# python run_benchmark.py turingdb
uv run python manage_servers.py turingdb stop

# Neo4j benchmark
uv run python manage_servers.py neo4j start
# python run_benchmark.py neo4j
uv run python manage_servers.py neo4j stop

# Memgraph benchmark
uv run python manage_servers.py memgraph start
# python run_benchmark.py memgraph
uv run python manage_servers.py memgraph stop
