#!/usr/bin/env bash

shopt -s expand_aliases

function check_result() {
    res=$?
    if [ $res -ne 0 ]; then
        if [ $res -ne 2 ]; then
            # If error is not 'already exists', this is a critical failure
            exit 1
        fi
    fi
}

if [ $# -ne 1 ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

DATASET=$1

script_dir=$(dirname $0)
cd $script_dir

bench neo4j stop || true
bench memgraph stop || true
bench turingdb stop || true

./0_download.sh $DATASET
check_result

./1_migrate.sh $DATASET
check_result

./2_gen_cypher.sh $DATASET
check_result

./3_gen_jsonl.sh $DATASET
check_result

./4_load_in_memgraph.sh $DATASET
check_result

./5_load_in_turingdb.sh $DATASET
check_result
