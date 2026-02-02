#!/usr/bin/env bash

set -e
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

# Check if TURING_HOME is set
if [ -z "$TURING_HOME" ]; then
    echo "TURING_HOME is not set. Please set it to the TuringDB installation directory."
    exit 1
fi

tdb="$TURING_HOME/bin/turingdb"

# Load reactome in turingdb
TURINGDB_DIR="$REPO_ROOT/install/turingdb"

if [ -d "$TURINGDB_DIR" ]; then
    echo "TuringDB directory already exists at $TURINGDB_DIR"
    echo "Removing existing TuringDB directory..."
    rm -rf "$TURINGDB_DIR"
fi

mkdir -p "$TURINGDB_DIR/data"
mkdir -p "$TURINGDB_DIR/graphs"
cp "$NEO4J_IMPORT/reactome.dump" "$TURINGDB_DIR/data/reactome.dump"

echo "Loading Reactome dump into turingdb..."
# Run in truly clean environment - only preserve HOME and basic shell info
env -i HOME="$HOME" TURING_HOME=$TURING_HOME bash -l -c "echo 'LOAD NEO4J '\''reactome.dump'\'' AS reactome' | '$tdb' -turing-dir '$TURINGDB_DIR'"
