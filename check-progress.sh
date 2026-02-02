#!/usr/bin/env bash

uv run servers_python/manage_servers.py neo4j start 2>&1 > /dev/null
neooutput=$(cypher-shell 'MATCH (n) RETURN count(n); MATCH ()-[r]->() RETURN count(r);')
nodeCount=$(echo "$neooutput" | head -n 2 | tail -n 1)
edgeCount=$(echo "$neooutput" | tail -n 1)
uv  run servers_python/manage_servers.py neo4j stop 2>&1 > /dev/null

while true; do
    memoutput=$(echo 'MATCH (n) RETURN count(n); MATCH ()-[r]->() RETURN count(r);' | mgconsole --port 7688)
    curNodeCount=$(echo "$memoutput" | head -n 4 | tail -n 1 | cut -d ' ' -f 2)
    curEdgeCount=$(echo "$memoutput" | tail -n 2 | head -n 1 | cut -d ' ' -f 2)
    nodeCountPercent=$((curNodeCount * 100 / nodeCount))
    edgeCountPercent=$((curEdgeCount * 100 / edgeCount))
    
    printf "\r- Progress: %d/%d nodes (%d%%) and %d/%d edges (%d%%)" \
           "$curNodeCount" "$nodeCount" "$nodeCountPercent" \
           "$curEdgeCount" "$edgeCount" "$edgeCountPercent"
    
    [[ $curNodeCount -eq $nodeCount && $curEdgeCount -eq $edgeCount ]] && break
    sleep 2
done

echo
