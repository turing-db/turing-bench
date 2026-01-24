#!/bin/bash

# open_tmux_session_memgraph.sh

set -e

SCRIPT_PATH=../open_tmux_session.sh

# Make open_tmux_session.sh script executable if it isn't already
chmod +x "$SCRIPT_PATH"

./$SCRIPT_PATH benchmark-memgraph-server start_memgraph.sh "You are running Memgraph v"

echo ""
echo "benchmark-memgraph-server session started! Use 'tmux ls' to see it."