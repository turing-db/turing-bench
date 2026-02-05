#!/usr/bin/env bash

set -e
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

JSON_FILE=/tmp/output.json
TDB_CYPHER_FILE=reactome.tbdcypher
SAVE_PATH="$DUMPS/reactome.turingdb"

if [ -d "$SAVE_PATH" ]; then
    echo "Reactome dump already exists in $SAVE_PATH. Skipping..."
    exit 1
fi

if [ -L "$TURINGDB_DIR" ]; then
    echo "Removing old TuringDB symbolic link..."
    rm "$TURINGDB_DIR"
elif [ -d "$TURINGDB_DIR" ]; then
    echo "Removing existing TuringDB directory..."
    rm -r "$TURINGDB_DIR"
fi

mkdir -p $TURINGDB_DATA_DIR
mkdir -p $TURINGDB_GRAPHS_DIR

echo "Loading Reactome json into turingdb..."
uv run "$SCRIPTS/cypher-to-turingdb-cypher.py" $JSON_FILE --output-file "$TURINGDB_DATA_DIR/$TDB_CYPHER_FILE"

# Create TuringDB graph using generated cypher script
uv run turingdb -turing-dir $TURINGDB_DIR < "$TURINGDB_DATA_DIR/$TDB_CYPHER_FILE"
echo "Reactome successfully created in TuringDB."

cp -r "$TURINGDB_DIR" "$SAVE_PATH"
echo "Reactome dump successfully stored in $SAVE_PATH directory."
