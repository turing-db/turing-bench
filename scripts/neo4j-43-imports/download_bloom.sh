#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="bloom.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/bloom/raw/refs/heads/main/data/bloom-43.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading bloom dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "bloom dump downloaded."
else
    echo "bloom dump already exists at $DUMP_FILE"
fi
