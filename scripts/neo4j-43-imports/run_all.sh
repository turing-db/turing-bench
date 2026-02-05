#!/usr/bin/env bash

set -e
shopt -s expand_aliases

if [ $# -ne 1 ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

DATASET=$1

script_dir=$(dirname $0)

cd $script_dir

./0_download.sh $DATASET
./1_migrate.sh $DATASET
./2_gen_cypher.sh $DATASET
./3_gen_jsonl.sh $DATASET
./4_load_in_memgraph.sh $DATASET
./5_load_in_turingdb.sh $DATASET
