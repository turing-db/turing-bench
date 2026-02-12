#!/usr/bin/env bash

set -e -o pipefail
shopt -s expand_aliases

GIT_ROOT="$(git rev-parse --show-toplevel)"
source "$GIT_ROOT/env.sh"

DATASET=${1-reactome}
QUERY_FILE=${2-queries_$DATASET.cypher}
QUERY_FILE_PATH="$QUERIES_DIR/$DATASET/$QUERY_FILE"

if [ ! -f $QUERY_FILE_PATH ]; then
    echo "Query file $QUERY_FILE_PATH does not exist"
    exit 1
fi

cd $SCRIPTS
alias uvrun="uv run --directory $GIT_ROOT python -m turingbench"

REPORT_DIR="$GIT_ROOT/reports"
mkdir -p "$REPORT_DIR"
REPORT_FILE="$REPORT_DIR/${DATASET}_benchmark_report.txt"

# Run benchmarks and capture output to report file (while still printing to stdout)
{

echo "- Stopping all databases"
bench turingdb stop || true > /dev/null
bench neo4j stop || true > /dev/null
bench memgraph stop || true > /dev/null

echo "- Switching to dataset $DATASET"
$SCRIPTS/switch-neo4j-dataset.sh $DATASET

echo "- Running benchmark for 'turingdb'"
bench turingdb start -- -turing-dir "$DUMPS/$DATASET.turingdb" -load "$DATASET"
uvrun turingdb --query-file $QUERY_FILE_PATH --database=$DATASET
bench turingdb stop

echo "- Running benchmark for 'neo4j'"
bench neo4j start
uvrun neo4j --query-file $QUERY_FILE_PATH
bench neo4j stop

echo "- Running benchmark for 'memgraph'"
bench memgraph start -- --data-directory=$DUMPS/$DATASET.memgraph
uvrun memgraph --query-file $QUERY_FILE_PATH --database=memgraph --url=bolt://localhost:7688
bench memgraph stop


} 2>&1 | tee "$REPORT_FILE"

echo "- Generating summary report"
uv run --directory "$GIT_ROOT" python "$GIT_ROOT/report_summary/parse_benchmark_report.py" \
    "$REPORT_FILE" --dataset "$DATASET" --update-readme
