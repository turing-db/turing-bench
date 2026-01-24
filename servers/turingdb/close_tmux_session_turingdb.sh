#!/bin/bash

set -e

SCRIPT_PATH=../close_tmux_session.sh
chmod +x "$SCRIPT_PATH"

./$SCRIPT_PATH benchmark-turingdb-server stop_turingdb.sh "Terminating server"

echo ""
echo "benchmark-turingdb-server session stopped!"