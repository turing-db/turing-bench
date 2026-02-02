#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="simpledb-4.3.dump"  # "reactome.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
DUMP_URL="s3://turing-internal/simpledb-4.3.dump"  # "https://reactome.org/download/current/reactome.graphdb.dump"

# Download dump if not exists
if [ ! -f $DUMP_PATH ]; then
    echo "Downloading Reactome dump..."
    # wget -O "$DUMP_PATH" "$DUMP_URL"
    aws s3 cp $DUMP_URL $DUMP_PATH
    echo "Reactome dump downloaded."
else
    echo "Reactome dump already exists at $DUMP_FILE"
fi