#pragma once

shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)

source "$REPO_ROOT/env.sh"

# Reactome
aws s3 sync --profile turingdb_intern $REPO_ROOT/dumps/reactome.turingdb s3://turingdb-external/bench-datasets/reactome.turingdbg
aws s3 sync --profile turingdb_intern $REPO_ROOT/dumps/reactome.memgraph s3://turingdb-external/bench-datasets/reactome.memgraphg
aws s3 sync --profile turingdb_intern $REPO_ROOT/dumps/reactome.neo4j s3://turingdb-external/bench-datasets/reactome.neo4jg

# PoleDB
aws s3 sync --profile turingdb_intern $REPO_ROOT/dumps/poledb.turingdb s3://turingdb-external/bench-datasets/poledb.turingdbg
aws s3 sync --profile turingdb_intern $REPO_ROOT/dumps/poledb.memgraph s3://turingdb-external/bench-datasets/poledb.memgraphg
aws s3 sync --profile turingdb_intern $REPO_ROOT/dumps/poledb.neo4j s3://turingdb-external/bench-datasets/poledb.neo4jg
