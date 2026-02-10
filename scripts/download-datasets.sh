#pragma once

shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)

source "$REPO_ROOT/env.sh"

# Reactome
if [ ! -d "$REPO_ROOT/dumps/reactome.turingdb" ]; then
    aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/reactome.turingdbg $REPO_ROOT/dumps/reactome.turingdb 
fi

if [ ! -d "$REPO_ROOT/dumps/reactome.memgraph" ]; then
    aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/reactome.memgraphg $REPO_ROOT/dumps/reactome.memgraph
fi

if [ ! -d "$REPO_ROOT/dumps/reactome.neo4j" ]; then
    aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/reactome.neo4jg $REPO_ROOT/dumps/reactome.neo4j
fi

# PoleDB
if [ ! -d "$REPO_ROOT/dumps/poledb.turingdb" ]; then
    aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/poledb.turingdbg $REPO_ROOT/dumps/poledb.turingdb
fi

if [ ! -d "$REPO_ROOT/dumps/poledb.memgraph" ]; then
    aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/poledb.memgraphg $REPO_ROOT/dumps/poledb.memgraph
fi

if [ ! -d "$REPO_ROOT/dumps/poledb.neo4j" ]; then
    aws s3 sync --profile turingdb_intern s3://turingdb-external/bench-datasets/poledb.neo4jg $REPO_ROOT/dumps/poledb.neo4j
fi
