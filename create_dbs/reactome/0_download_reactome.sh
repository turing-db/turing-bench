#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="$NEO4J_IMPORT/reactome.dump"
DUMP_URL="https://reactome.org/download/current/reactome.graphdb.dump"

# Download dump if not exists
if [ ! -f "$DUMP_FILE" ]; then
    echo "Downloading Reactome dump..."
    wget -O "$DUMP_FILE" "$DUMP_URL"
    echo "Reactome dump downloaded."
else
    echo "Reactome dump already exists at $DUMP_FILE"
fi