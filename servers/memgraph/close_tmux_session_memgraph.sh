#!/bin/bash

set -e

SCRIPT_PATH=../close_tmux_session.sh
chmod +x "$SCRIPT_PATH"

./$SCRIPT_PATH benchmark-memgraph-server stop_memgraph.sh

echo ""
echo "benchmark-memgraph-server session stopped!"