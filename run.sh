#!/usr/bin/env bash

set -e
shopt -s expand_aliases

GIT_ROOT="$(git rev-parse --show-toplevel)"
source "$GIT_ROOT/env.sh"

DATASET=${1-reactome}
QUERY_FILE=${2-queries_$DATASET.cypher}
QUERY_FILE_PATH="$QUERIES_DIR/$DATASET/$QUERY_FILE"

if [ ! -f $QUERY_FILE_PATH ]; then
    echo "Query file $QUERY_FILE_PATH does not exist"
    exit 1
fi

cd $SCRIPTS
alias uvrun="uv run --directory $GIT_ROOT python -m turingbench"

bench turingdb stop > /dev/null || true
bench neo4j stop > /dev/null || true
bench memgraph stop > /dev/null || true

$SCRIPTS/switch-dataset.sh $DATASET turingdb
$SCRIPTS/switch-dataset.sh $DATASET neo4j
$SCRIPTS/switch-dataset.sh $DATASET memgraph

# TuringDB benchmark
bench turingdb start || true
uvrun turingdb --query-file $QUERY_FILE_PATH
bench turingdb stop

# Neo4j benchmark
bench neo4j start
uvrun neo4j --query-file $QUERY_FILE_PATH
bench neo4j stop

# Memgraph benchmark
bench memgraph start
uvrun memgraph --query-file $QUERY_FILE_PATH --database=memgraph --url=bolt://localhost:7688
bench memgraph stop
