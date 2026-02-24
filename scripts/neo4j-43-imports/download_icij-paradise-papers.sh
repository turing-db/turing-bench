#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="icij-paradise-papers.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/icij-paradise-papers/raw/refs/heads/main/data/icij-paradise-papers-43.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading icij-paradise-papers dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "icij-paradise-papers dump downloaded."
else
    echo "icij-paradise-papers dump already exists at $DUMP_FILE"
fi
