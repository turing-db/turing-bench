cd $ACTIVE_REPO/src/external/neo4j

tar -xvf neo4j-4.3.23.tar.gz

export NEO4JDIR=$ACTIVE_REPO/src/external/neo4j/neo4j-community-4.3.23-SNAPSHOT

cd $NEO4JDIR/data/databases

rm -rf graph.db

wget https://reactome.org/download/current/reactome.graphdb.tgz

tar -xzvf reactome.graphdb.tgz

echo "dbms.default_database=graph.db" >> $NEO4JDIR/conf/neo4j.conf
echo "dbms.recovery.fail_on_missing_files=false" >> $NEO4JDIR/conf/neo4j.conf
echo "unsupported.dbms.tx_log.fail_on_corrupted_log_files=false" >> $NEO4JDIR/conf/neo4j.conf
echo "dbms.security.auth_enabled=false" >> $NEO4JDIR/conf/neo4j.conf

cd $NEO4JDIR
bin/neo4j start

bin/neo4j restart
