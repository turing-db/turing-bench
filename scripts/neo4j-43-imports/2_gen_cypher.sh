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
FILE_PATH="$DUMPS/$DATASET.cypher"

if [ -f $FILE_PATH ]; then
    echo "- $FILE_PATH already exists. Skipping..."
    exit 1
fi

bench neo4j start || true

start=`date +%s`

# Export constraints
echo "- Exporting constraints/indexes from neo4j..."

cypher-shell "SHOW CONSTRAINTS 
YIELD type, entityType, labelsOrTypes AS l, properties AS p 
WHERE type = 'UNIQUENESS' AND entityType = 'NODE' AND size(p) = 1
RETURN l[0] AS label, p[0] AS property;" | \
sed '/---------.*/d' | \
awk -F', ' 'NR > 1 {
    gsub(/"/, "", $1);
    gsub(/"/, "", $2);
    if ($1 && $2)
        print "CREATE CONSTRAINT ON (node:" $1 ") ASSERT node." $2 " IS UNIQUE;"
}' > $FILE_PATH

# Export indexes
cypher-shell "SHOW INDEXES 
YIELD type, entityType, labelsOrTypes AS l, properties AS p, owningConstraint WHERE entityType = 'NODE' AND size(p) = 1
RETURN type, l[0] AS label, p[0] AS property;" | \
sed '/---------.*/d' | \
awk -F', ' 'NR > 1 {
    gsub(/"/, "", $2);
    gsub(/"/, "", $3);
    if ($2 && $3)
        print "CREATE INDEX ON :" $2 "(" $3 ");"
}' >> $FILE_PATH

echo "- Exporting constraints/indexes took $(elapsed $start)"

# Export nodes/edges
start=`date +%s`
echo "- Exporting nodes/edges from neo4j..."
cypher-shell 'CALL apoc.export.cypher.all("script.cypher", {
    format: "plain",
    cypherFormat: "create",
    useOptimizations: { type: "UNWIND_BATCH", unwindBatchSize: 1000 }
})
YIELD file, batches, source, format, nodes, relationships, properties, time, rows, batchSize
RETURN file, batches, source, format, nodes, relationships, properties, time, rows, batchSize;'

mv "$NEO4J_IMPORT/script.cypher" /tmp

sed -i 's/CREATE.*INDEX.*FOR (.*:\(.*\)) ON (.*\.\(.*\))/CREATE INDEX ON :\1(\2)/' /tmp/script.cypher
sed -i 's/CREATE CONSTRAINT.*FOR (.*:\(.*\)).*REQUIRE.*(.*\.\(.*\)) IS UNIQUE;/CREATE CONSTRAINT ON (node:\1) ASSERT node.\2 IS UNIQUE;\nCREATE INDEX ON :\1(\2);/' /tmp/script.cypher
sed -i 's/DROP CONSTRAINT.*//' /tmp/script.cypher

echo "- Exporting nodes/edges took $(elapsed $start)"

start=`date +%s`

echo "- Writing full script to $FILE_PATH..."
cat /tmp/script.cypher >> $FILE_PATH
echo "- Writing full script took $(elapsed $start)"

