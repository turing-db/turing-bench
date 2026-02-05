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
SCRIPT="download_$DATASET.sh"

# Run download script
bash "$SCRIPT"
