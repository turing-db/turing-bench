#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="healthcare-analytics.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/healthcare-analytics/raw/refs/heads/main/data/healthcare-analytics-44.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading healthcare-analytics dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "healthcare-analytics dump downloaded."
else
    echo "healthcare-analytics dump already exists at $DUMP_FILE"
fi
