#!/usr/bin/env bash

set -e
shopt -s expand_aliases
REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

JSON_FILE=$DUMPS/reactome.jsonl
SAVE_PATH="$DUMPS/reactome.turingdb"

if [ -d "$SAVE_PATH" ]; then
    echo "- Reactome dump already exists in $SAVE_PATH. Skipping..."
    exit 1
fi

echo "- Loading Reactome json into turingdb..."
mkdir -p $SAVE_PATH/data
cp "$JSON_FILE" "$SAVE_PATH/data/output.json"

start=$(date +%s)
echo "LOAD JSONL 'output.json' AS reactome;" | turingdb -turing-dir $SAVE_PATH
echo "- Loading Reactome jsonl into turingdb took $(elapsed $start)"

