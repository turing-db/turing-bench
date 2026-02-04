#!/usr/bin/env bash

set -euo pipefail
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

if [ $# -ne 1 ]; then
    echo "usage: $0 <dataset-name>"
    exit 1
fi

dataset=$1

dump_src="$DUMPS/$dataset.neo4j"
dump_dst="$NEO4J_DATA_DIR"

if [ ! -d "$dump_src" ]; then
    echo "dump path $dump_src does not exist"
    exit 1
fi

if [ -d "$dump_dst" ]; then
    echo "Removing existing dump at $dump_dst"
    rm -r "$dump_dst"
fi

ln -s $dump_src $dump_dst
ls -l "$dump_dst" --color=always
