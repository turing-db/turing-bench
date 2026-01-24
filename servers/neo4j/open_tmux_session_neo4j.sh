#!/bin/bash

set -e

SCRIPT_PATH=../open_tmux_session.sh

# Make open_tmux_session.sh script executable if it isn't already
chmod +x "$SCRIPT_PATH"

./$SCRIPT_PATH benchmark-neo4j-server start_neo4j.sh "Started neo4j"

echo ""
echo "benchmark-neo4j-server session started! Use 'tmux ls' to see it."