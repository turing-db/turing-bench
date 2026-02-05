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
FILE_PATH="$DUMPS/$DATASET.jsonl"

bench neo4j start || true

start=`date +%s`

if [ -f $FILE_PATH ]; then
    echo "- $FILE_PATH already exists. Skipping..."
    exit 1
fi

# Export graph as jsonl file
start=`date +%s`
cypher-shell 'CALL apoc.export.json.all("output.json",{useTypes:true});'
mv "$NEO4J_IMPORT/output.json" $FILE_PATH
echo "- Exporting nodes/edges took $(elapsed $start)"
