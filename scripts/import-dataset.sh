#!/usr/bin/env bash

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

datasets="poledb reactome"

if [ -z "$1" ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

dataset="$1"

echo $datasets | grep -w -q $dataset
inlist=$(echo $?)

if [ $inlist -ne 0 ]; then
    echo "- Dataset '$dataset' does not exist."
    echo "- Available datasets:"

    for d in ${datasets[@]}; do
        echo " - $d"
    done

    exit 1
fi


echo "Importing '$dataset'..."

$REPO_ROOT/scripts/neo4j-43-imports/run_all.sh $dataset

