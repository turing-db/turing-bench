#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="fincen.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/fincen/raw/refs/heads/main/data/fincen-43.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading fincen dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "fincen dump downloaded."
else
    echo "fincen dump already exists at $DUMP_FILE"
fi
