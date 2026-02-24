#!/usr/bin/env bash

shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)

source "$REPO_ROOT/env.sh"

function download_dataset() {
    local dataset=$1
    if [ ! -d "$REPO_ROOT/dumps/$dataset.turingdb" ]; then
        aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/$dataset.turingdb $REPO_ROOT/dumps/$dataset.turingdb
    fi

    if [ ! -d "$REPO_ROOT/dumps/$dataset.memgraph" ]; then
        aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/$dataset.memgraph $REPO_ROOT/dumps/$dataset.memgraph
    fi

    if [ ! -d "$REPO_ROOT/dumps/$dataset.neo4j" ]; then
        aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/$dataset.neo4j $REPO_ROOT/dumps/$dataset.neo4j
    fi

    if [ ! -f "$REPO_ROOT/dumps/$dataset.jsonl" ]; then
        aws s3 cp --profile turingdb_intern s3://turingdb-external/bench-datasets/$dataset.jsonl $REPO_ROOT/dumps/$dataset.jsonl
    fi
}

download_dataset "reactome"
download_dataset "poledb"
