#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="wwc2019.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/wwc2019/raw/refs/heads/main/data/wwc2019-43.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading wwc2019 dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "wwc2019 dump downloaded."
else
    echo "wwc2019 dump already exists at $DUMP_FILE"
fi
