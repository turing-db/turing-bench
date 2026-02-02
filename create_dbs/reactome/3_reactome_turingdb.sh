#!/usr/bin/env bash

set -e
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

JSON_FILE=/tmp/output.json
TDB_CYPHER_FILE=simpledb.tbdcypher  # reactome.tbdcypher

# Check if TURING_HOME is set
if [ -z "$TURING_HOME" ]; then
    echo "TURING_HOME is not set. Please set it to the TuringDB installation directory."
    exit 1
fi

# Load reactome in turingdb
if [ -d "$TURINGDB_DIR" ]; then
    echo "TuringDB directory already exists at $TURINGDB_DIR"
    echo "Removing existing TuringDB directory..."
    rm -rf "$TURINGDB_DIR"
fi

mkdir -p $TURINGDB_DATA_DIR
mkdir -p $TURINGDB_GRAPHS_DIR

echo "Loading Reactome json into turingdb..."
uv run "$SCRIPTS/cypher-to-turingdb-cypher.py" $JSON_FILE --output-file "$TURINGDB_DATA_DIR/$TDB_CYPHER_FILE"

# Create TuringDB graph using generated cypher script
uv run turingdb -turing-dir $TURINGDB_DIR < "$TURINGDB_DATA_DIR/$TDB_CYPHER_FILE"
echo "Reactome successfully created in TuringDB."
