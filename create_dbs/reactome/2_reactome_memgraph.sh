#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

SAVE_PATH="$DUMPS/reactome.memgraph"

if [ -d "$SAVE_PATH" ]; then
    echo "Reactome dump already exists in $SAVE_PATH. Skipping..."
    exit 1
fi

# Convert Neo4j dump to memgraph using Cypher script
"$SCRIPTS/neo4j-to-memgraph-cypher.sh"
echo "Conversion from Neo4j dump to memgraph done."

cp -r "$MEMGRAPH_DATA_DIR" "$SAVE_PATH"
echo "Reactome dump successfully stored in $SAVE_PATH directory."
