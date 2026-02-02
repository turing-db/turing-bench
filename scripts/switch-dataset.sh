#!/usr/bin/env bash

set -euo pipefail
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

if [ $# -ne 2 ]; then
    echo "usage: $0 <dataset-name> <turingdb|neo4j|memgraph>"
    exit 1
fi

dataset=$1
target=$2

dump_src="$DUMPS/$dataset"
dump_dst=""
if [ "$target" == "turingdb" ]; then
    dump_src="$dump_src.turingdb"
    dump_dst="$TURINGDB_DIR"
elif [ "$target" == "neo4j" ]; then
    dump_src="$dump_src.neo4j"
    dump_dst="$NEO4J_DATA_DIR"
elif [ "$target" == "memgraph" ]; then
    dump_src="$dump_src.memgraph"
    dump_dst="$MEMGRAPH_DATA_DIR"
else
    echo "unknown target $target"
    exit 1
fi

if [ ! -d "$dump_src" ]; then
    echo "dump path $dump_src does not exist"
    exit 1
fi

if [ -d "$dump_dst" ]; then
    echo "Removing existing dump at $dump_dst"
    rm -r "$dump_dst"
fi

ln -s "$dump_src" "$dump_dst"
ls -l "$dump_dst" --color=always

