#!/usr/bin/env bash

set -e
shopt -s expand_aliases
REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

DATASET=$1
JSON_FILE="$DUMPS/$DATASET.jsonl"
SAVE_PATH="$DUMPS/$DATASET.turingdb"

if [ -d "$SAVE_PATH" ]; then
    echo "- $DATASET dump already exists in $SAVE_PATH. Skipping..."
    exit 2
fi

echo "- Loading $DATASET jsonl into turingdb..."
mkdir -p $SAVE_PATH/data
cp "$JSON_FILE" "$SAVE_PATH/data/output.json"

start=$(date +%s)
echo "LOAD JSONL 'output.json' AS $DATASET;" | uv run turingdb -turing-dir $SAVE_PATH
echo "- Loading $DATASET jsonl into turingdb took $(elapsed $start)"
rm "$SAVE_PATH/data/output.json"

