#!/usr/bin/env bash

set -e
shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"
SAVE_PATH="$DUMPS/reactome.memgraph"
SCRIPT_PATH="$DUMPS/reactome.cypher"

if [ -d "$SAVE_PATH" ]; then
    echo "Reactome data folder already exists in $SAVE_PATH. Skipping..."
    exit 1
fi

# Ensure memgraph is stopped
bench memgraph stop || true

# Start memgraph using the data folder
bench memgraph start -- --data-directory="$SAVE_PATH"

# Import data
start=`date +%s`
echo "- Importing script in memgraph..."

mgconsole --port 7688 < $SCRIPT_PATH &

"$SCRIPTS/check-progress.sh"

bench memgraph stop

end=`date +%s`
runtime=$((end-start))
echo "$- Importing script took $(elapsed $start)"
