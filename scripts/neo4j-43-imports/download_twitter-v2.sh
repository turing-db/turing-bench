#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="twitter-v2.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/twitter-v2/raw/refs/heads/main/data/twitter-v2-43.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading twitter-v2 dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "twitter-v2 dump downloaded."
else
    echo "twitter-v2 dump already exists at $DUMP_FILE"
fi
