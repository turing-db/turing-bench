#!/bin/bash

# stop_neo4j.sh

tmux send-keys -t "benchmark-neo4j-server" "cd ~/turing-bench/install && source env.sh && cd ~/turing-bench/servers/neo4j && neo4j stop" C-m