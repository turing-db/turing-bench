#!/bin/bash

set -e

SCRIPT_PATH=../close_tmux_session.sh
chmod +x "$SCRIPT_PATH"

./$SCRIPT_PATH benchmark-neo4j-server stop_neo4j.sh "Stopping Neo4j............ stopped"

echo ""
echo "benchmark-neo4j-server session stopped!"