#!/bin/bash

# start_neo4j.sh

set -e

cd ~/turing-bench/install
source env.sh
neo4j start

echo "Neo4j successfully started."