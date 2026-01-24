#!/bin/bash

# open_tmux_session_turingdb.sh

set -e

SCRIPT_PATH=../open_tmux_session.sh

# Make open_tmux_session.sh script executable if it isn't already
chmod +x "$SCRIPT_PATH"

./$SCRIPT_PATH benchmark-turingdb-server start_turingdb.sh "Server listening"

echo ""
echo "benchmark-turingdb-server session started! Use 'tmux ls' to see it."