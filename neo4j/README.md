This directory contains information for running comparable benchmarks against Neo4j.

1. Extract Neo4j Instance
```
cd $TURINGDBDIR/external/neo4j && tar -xvf neo4j-4.3.23.tar.gz
```
Herein, `$NEO4JDIR = $TURINGDBDIR/external/neo4j/neo4j-community-4.3.23-SNAPSHOT`, i.e. the directory which Neo4j was just extracted into.

2. Get fresh Reactome into Neo4j
```
cd $NEO4JDIR/data/databases
rm graph.db
wget https://reactome.org/download/current/reactome.graphdb.tgz
tar -xzvf reactome.graphdb.tgz
```
I needed to remove the old `graph.db` and replace it with the new one, which the `tar` extraction provides.

3. Configure Neo4j
```
echo "dbms.default_database=graph.db" >> $NEO4JDIR/conf/neo4j.conf

echo "dbms.recovery.fail_on_missing_files=false" >> $NEO4JDIR/conf/neo4j.conf

echo "unsupported.dbms.tx_log.fail_on_corrupted_log_files=false" >> $NEO4JDIR/conf/neo4j.conf
```
