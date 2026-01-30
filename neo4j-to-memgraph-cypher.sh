#!/usr/bin/env bash

set -euo pipefail

# Fail if mgconsole is installed
if [ ! command -v mgconsole &> /dev/null ]; then
    echo "! mgconsole was not found, please source the env.sh script"
    echo "! If mgconsole can still not be found, please install it with the ./install.sh"
    exit 1
fi

# Run neo4j if not already running
uv run servers_python/manage_servers.py neo4j start || true

start=`date +%s`
# Export constraints
echo "- Exporting constraints from neo4j..."
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
}' > ./output.cypher

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
}' >> ./output.cypher

end=`date +%s`
runtime=$((end-start))
echo "- Exporting constraints/indexes took $runtime seconds"

start=`date +%s`
# Export nodes/edges
echo "- Exporting nodes/edges from neo4j..."
cypher-shell 'CALL apoc.export.cypher.all("script.cypher", {
    format: "plain",
    cypherFormat: "create",
    useOptimizations: { type: "UNWIND_BATCH", unwindBatchSize: 1000 }
})
YIELD file, batches, source, format, nodes, relationships, properties, time, rows, batchSize
RETURN file, batches, source, format, nodes, relationships, properties, time, rows, batchSize;'

sed -i '/.*CREATE CONSTRAINT.*/d' ./install/neo4j-build/import/script.cypher
sed -i '/.*CREATE .* INDEX.*/d' ./install/neo4j-build/import/script.cypher

end=`date +%s`
runtime=$((end-start))
echo "- Exporting nodes/edges took $runtime seconds"

start=`date +%s`
echo "- Writing full script to output.cypher..."
cat ./install/neo4j-build/import/script.cypher >> ./output.cypher
end=`date +%s`
runtime=$((end-start))
echo "- Writing full script took $runtime seconds"

# Stop neo4j
uv run servers_python/manage_servers.py neo4j stop || true

# Ensure memgraph is stopped
uv run servers_python/manage_servers.py memgraph stop || true

# Removing old memgraph data dir
start=`date +%s`
echo "- Removing old memgraph data dir..."
rm -rf ./install/memgraph/data
end=`date +%s`
runtime=$((end-start))
echo "- Removing old memgraph data dir took $runtime seconds"

# Start memgraph
uv run servers_python/manage_servers.py memgraph start || true

# Import script
start=`date +%s`
echo "- Importing script in memgraph..."

mgconsole --port 7688 < ./output.cypher
end=`date +%s`
runtime=$((end-start))
echo "- Importing script took $runtime seconds"
