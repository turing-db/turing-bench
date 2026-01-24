#!/bin/bash

set -e

cd ~/turing-bench/servers

print_tool_header() {
    echo ""
    echo "╔════════════════════════════════╗"
    echo "║ $1"
    echo "╚════════════════════════════════╝"
    echo ""
}

print_section_header() {
    echo ""
    echo "--- $1 ---"
    echo ""
}

# TuringDB
print_tool_header "TuringDB"
cd turingdb
print_section_header "Starting"
./open_tmux_session_turingdb.sh
print_section_header "Stopping"
./close_tmux_session_turingdb.sh

# Neo4j
print_tool_header "Neo4j"
cd ../neo4j
print_section_header "Starting"
./open_tmux_session_neo4j.sh
print_section_header "Stopping"
./close_tmux_session_neo4j.sh

# Memgraph
print_tool_header "Memgraph"
cd ../memgraph
print_section_header "Starting"
./open_tmux_session_memgraph.sh
print_section_header "Stopping"
./close_tmux_session_memgraph.sh

# Final message
print_tool_header "Complete"
echo "All servers started and stopped successfully!"