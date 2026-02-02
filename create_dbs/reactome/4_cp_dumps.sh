#!/usr/bin/env bash

set -e
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

if [ -z "$DUMPS" ]; then
    echo "DUMPS is not set. Please set it to the directory where dumps should be stored."
    exit 1
fi

if [ ! -d $DUMPS ]; then
    mkdir -p $DUMPS
    echo "$DUMPS directory created."
fi

if [ -d "$DUMPS/reactome.neo4j" ]; then
    rm -rf "$DUMPS/reactome.neo4j"
fi

if [ -d "$DUMPS/reactome.memgraph" ]; then
    rm -rf "$DUMPS/reactome.memgraph"
fi

if [ -d "$DUMPS/reactome.turingdb" ]; then
    rm -rf "$DUMPS/reactome.turingdb"
fi

cp -r "$NEO4J_DATA_DIR" "$DUMPS/reactome.neo4j"
cp -r "$MEMGRAPH_DATA_DIR" "$DUMPS/reactome.memgraph"
cp -r "$TURINGDB_DIR" "$DUMPS/reactome.turingdb"

echo "Neo4j, Memgraph and TuringDB data successfully stored in $DUMPS directory."