#!/usr/bin/env bash

shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

script_dir=$(dirname $0)
cd $script_dir

# List all download_x.sh scripts in this directory
echo "Available datasets:"
ls download_*.sh | sed 's/download_//g' | sed 's/.sh//g' | sed 's/^/  - /g'
