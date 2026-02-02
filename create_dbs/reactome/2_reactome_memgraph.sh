#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

# Convert Neo4j dump to memgraph using Cypher script
"$SCRIPTS/neo4j-to-memgraph-cypher.sh"
echo "Conversion from Neo4j dump to memgraph done."