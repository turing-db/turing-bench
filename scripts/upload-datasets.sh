#pragma once

shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)

source "$REPO_ROOT/env.sh"

function cleanup_memgraph() {
    rm -r "$REPO_ROOT/dumps/$1.memgraph/databases/memgraph/replication"
    rm -r "$REPO_ROOT/dumps/$1.memgraph/databases/memgraph/streams"
    rm -r "$REPO_ROOT/dumps/$1.memgraph/databases/memgraph/triggers"
    rm -r "$REPO_ROOT/dumps/$1.memgraph/databases/memgraph/snapshots"
}

function upload_dataset() {
    cleanup_memgraph "$1"
    aws s3 sync --profile turingdb_intern "$REPO_ROOT/dumps/$1.turingdb" s3://turingdb-external/bench-datasets/"$1".turingdb
    aws s3 sync --profile turingdb_intern "$REPO_ROOT/dumps/$1.memgraph" s3://turingdb-external/bench-datasets/"$1".memgraph
    aws s3 sync --profile turingdb_intern "$REPO_ROOT/dumps/$1.neo4j" s3://turingdb-external/bench-datasets/"$1".neo4j
}

upload_dataset reactome
upload_dataset poledb
