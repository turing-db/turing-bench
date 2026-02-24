#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="icij-offshoreleaks.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://github.com/neo4j-graph-examples/icij-offshoreleaks/raw/refs/heads/main/data/icij-offshoreleaks-43.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading icij-offshoreleaks dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "icij-offshoreleaks dump downloaded."
else
    echo "icij-offshoreleaks dump already exists at $DUMP_FILE"
fi
