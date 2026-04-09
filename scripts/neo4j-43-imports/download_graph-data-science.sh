#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="graph-data-science.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/graph-data-science/raw/refs/heads/main/data/graph-data-science-43.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading graph-data-science dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "graph-data-science dump downloaded."
else
    echo "graph-data-science dump already exists at $DUMP_FILE"
fi
