#!/usr/bin/env bash
set -euo pipefail  # Exit on error, unset vars, and fail on pipeline errors
IFS=$'\n\t'

NEO4J_TAR="neo4j-4.3.23.tar.gz"
NEO4J_DIRNAME="neo4j-community-4.3.23-SNAPSHOT"
NEO4J_DOWNLOAD_DIR="${ACTIVE_REPO:?}/src/external/neo4j"
NEO4JDIR="${NEO4J_DOWNLOAD_DIR}/${NEO4J_DIRNAME}"
GRAPHDB_URL="https://reactome.org/download/current/reactome.graphdb.tgz"
GRAPHDB_TAR="reactome.graphdb.tgz"
DB_DIR="${NEO4JDIR}/data/databases"
CONF_FILE="${NEO4JDIR}/conf/neo4j.conf"

echo "Please ensure your current workspace (cwk, \$ACTIVE_REPO) is set to a TuringDB repo."

# Check paths
[ -d "$NEO4J_DOWNLOAD_DIR" ] || { echo "Directory $NEO4J_DOWNLOAD_DIR not found. Is your current workspace a TuringDB repo?"; exit 1; }

# Extract Neo4j
cd "$NEO4J_DOWNLOAD_DIR"

# Check if Neo4j already extracted, exit if so
if [ -d "$NEO4JDIR" ]; then
    echo "Directory $NEO4JDIR already exists. Please backup or remove, and rerun the script. Exiting."
    exit 0
fi

# Extract if not already (but this is redundant now with the above check)
if [ ! -d "$NEO4JDIR" ]; then
    [ -f "$NEO4J_TAR" ] || { echo "$NEO4J_TAR not found"; exit 1; }
    tar -xvf "$NEO4J_TAR"
fi

# From here, the Neo4j instance is fresh, and so we can safely remove
# anything without fear of deleting user data

# Setup DB directory
mkdir -p "$DB_DIR"
cd "$DB_DIR"

# Remove old DB safely
if [ -d "graph.db" ]; then
    echo "Removing existing graph.db..."
    rm -rf "graph.db"
fi

# Download new reactome
if [ ! -f "$GRAPHDB_TAR" ]; then
    echo "Downloading reactome..."
    wget -q --show-progress "$GRAPHDB_URL"
fi

# Verify download is a valid tar.gz
echo "Validating downloaded reactome"
if ! tar -tzf "$GRAPHDB_TAR" >/dev/null 2>&1; then
    echo "Downloaded $GRAPHDB_TAR is not a valid tar.gz"
    exit 1
fi

# Extract graphdb
echo "Extracting extracting reactome..."
tar -xzvf "$GRAPHDB_TAR"

# Update config
echo "Setting Neo4J config..."
{
    grep -qxF "dbms.default_database=graph.db" "$CONF_FILE" || echo "dbms.default_database=graph.db"
    grep -qxF "dbms.recovery.fail_on_missing_files=false" "$CONF_FILE" || echo "dbms.recovery.fail_on_missing_files=false"
    grep -qxF "unsupported.dbms.tx_log.fail_on_corrupted_log_files=false" "$CONF_FILE" || echo "unsupported.dbms.tx_log.fail_on_corrupted_log_files=false"
    grep -qxF "dbms.security.auth_enabled=false" "$CONF_FILE" || echo "dbms.security.auth_enabled=false"
} >> "$CONF_FILE"

# Start Neo4j
cd "$NEO4JDIR"
echo "Starting Neo4j..."
bin/neo4j start

echo "Sleeping 15 seconds before restarting Neo4j to load Reactome (bug fix)"
sleep 15

echo "Restarting Neo4j..."
bin/neo4j restart

echo "Setup complete! Please wait a few seconds for Neo4j to warm up before running benchmarks"
