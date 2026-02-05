#!/usr/bin/env bash

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NEO4J_HOME="/home/dev/turing-bench/install/neo4j-build"
DUMP_FILE="$SCRIPT_DIR/reactome.dump"
NEO4J_DATA_DIR="$NEO4J_HOME/data"
DUMP_URL="https://reactome.org/download/current/reactome.graphdb.dump"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../" && pwd)"

echo "=== Reactome Neo4j v5 Setup ==="

# cd $NEO4J_HOME
if [ -d "$NEO4J_DATA_DIR" ]; then
    echo "Remove neo4j data directory..."
    rm -r $NEO4J_DATA_DIR
else
    echo "Reactome neo4j data directory does not exist"
fi

# Step 1: Download dump if not exists
if [ ! -f "$DUMP_FILE" ]; then
    echo "Downloading Reactome dump..."
    wget -O "$DUMP_FILE" "$DUMP_URL"
else
    echo "Reactome dump already exists at $DUMP_FILE"
fi

# Copy reactome dump to neo4j import directory
cp $DUMP_FILE "$NEO4J_HOME/import/"

# Step 2: Extract and load the dump
echo "Loading Reactome dump into Neo4j..."
cd "$NEO4J_HOME"
source "$REPO_ROOT/env.sh"

# Load reactome in neo4j
cat ./import/reactome.dump | neo4j-admin database load --from-stdin neo4j --overwrite-destination=true

# Migrate reactome from neo4j v4 to v5 
neo4j-admin database migrate neo4j --verbose --force-btree-indexes-to-range

echo "=== Reactome Neo4j v5 Setup Complete ==="
echo "Data available at: $NEO4J_HOME/data/databases/"