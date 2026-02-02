#!/usr/bin/env bash

set -e
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DUMP_FILE="reactome.dump"
DUMP_PATH="$NEO4J_IMPORT/$DUMP_FILE"
SAVE_PATH="$DUMPS/reactome.neo4j"

if [ -d "$SAVE_PATH" ]; then
    echo "Reactome dump already exists in $SAVE_PATH. Skipping..."
    exit 1
fi

# Stop Neo4j
bench neo4j stop || true

# Remove Neo4j data directory
if [ -L "$NEO4J_DATA_DIR" ]; then
    echo "Removing old Neo4j data symbolic link..."
    rm $NEO4J_DATA_DIR
elif [ -d "$NEO4J_DATA_DIR" ]; then
    echo "Remove Neo4j data directory..."
    rm -r $NEO4J_DATA_DIR
else
    echo "Reactome neo4j data directory does not exist"
fi

# Load reactome in neo4j
echo "Loading Reactome dump into Neo4j..."
cat $DUMP_PATH | neo4j-admin database load --from-stdin neo4j --overwrite-destination=true
echo "Reactome successfully loaded in Neo4j."

# Migrate reactome from neo4j v4 to v5
neo4j-admin database migrate neo4j --verbose --force-btree-indexes-to-range
echo "Migration from Neo4j v4 to v5 done."

cp -r "$NEO4J_DATA_DIR" "$SAVE_PATH"
echo "Reactome dump successfully stored in $SAVE_PATH directory."
