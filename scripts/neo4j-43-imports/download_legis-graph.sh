#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="legis-graph.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/legis-graph/raw/refs/heads/main/data/legis-graph-43.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading legis-graph dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "legis-graph dump downloaded."
else
    echo "legis-graph dump already exists at $DUMP_FILE"
fi
