#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="reactome.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="https://reactome.org/download/current/reactome.graphdb.dump"

if [ -f "$DUMP_PATH" ]; then
    rm "$DUMP_PATH"
fi

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading Reactome dump..."
    wget -O "$DUMP_PATH" "$DUMP_URL"
    echo "Reactome dump downloaded."
else
    echo "Reactome dump already exists at $DUMP_FILE"
fi
