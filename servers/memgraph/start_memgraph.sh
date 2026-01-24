#!/bin/bash

# start_memgraph.sh

set -e
shopt -s expand_aliases

cd ~/turing-bench/install
source env.sh
memgraph --log-file=./memgraph/logs/memgraph.log --data-directory=./memgraph/data/ --bolt-port=7688
