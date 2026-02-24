#!/usr/bin/env bash

shopt -s expand_aliases

REPO_ROOT=$(git rev-parse --show-toplevel)
source "$REPO_ROOT/env.sh"

script_dir=$(dirname $0)
cd $script_dir

for f in $(ls download_*.sh); do
    dataset=$(echo $f | sed 's/download_//g' | sed 's/.sh//g')
    echo "- Importing '$dataset'"
    ./run_all.sh $dataset
done
