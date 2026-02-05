#!/usr/bin/env bash

set -e
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <dataset>"
    exit 1
fi

DATASET=$1
SAVE_PATH="$DUMPS/$DATASET.memgraph"
SCRIPT_PATH="$DUMPS/$DATASET.cypher"

if [ -d "$SAVE_PATH" ]; then
    echo "$DATASET data folder already exists in $SAVE_PATH. Skipping..."
    exit 2
fi

# Ensure memgraph is stopped
bench memgraph stop || true

# Start memgraph using the data folder
bench memgraph start -- --data-directory="$SAVE_PATH"

# Import data
start=`date +%s`
echo "- Importing script in memgraph..."

mgconsole --port 7688 < $SCRIPT_PATH

"$SCRIPTS/check-progress.sh"

bench memgraph stop

end=`date +%s`
runtime=$((end-start))
echo "- Importing script took $(elapsed $start)"
