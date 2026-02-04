#!/usr/bin/env bash

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

DATASET_DIR="$REPO_ROOT/create_dbs"

if [ -z "$1" ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

dataset="$1"

if [ ! -d "$DATASET_DIR/$dataset" ]; then
    echo "Dataset $dataset does not exist."
    exit 1
fi


echo "Importing '$dataset'..."

$DATASET_DIR/$dataset/0_download_$1.sh || true
$DATASET_DIR/$dataset/1_$1_neo4j.sh || true
$DATASET_DIR/$dataset/2_create_cypher_script.sh || true
$DATASET_DIR/$dataset/3_create_jsonl_file.sh || true
$DATASET_DIR/$dataset/4_$1_memgraph.sh || true
$DATASET_DIR/$dataset/5_$1_turingdb.sh || true
