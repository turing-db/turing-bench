This directory contains information for running comparable benchmarks against Neo4j.

# Usage
## Setup script (Preferred)
`setup.sh` should contain all the required set up steps to go from nothing to a running Neo4j instance with Reactome loaded. However, if there are problems with the script, or you would like to perform the setup manually, the explanation of the script steps can be found below.

Otherwise, after running `setup.sh`, 
- Create and build the Python virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You are then ready to run the benchmark script, example usage:
```
python3 bench.py --query "samples/neo4j-str-prop-multihop.cypher" --runs 3
```

Use `python3 bench.py -h` for argument explanations.

## Manual
1. Extract Neo4j Instance
```
cd $TURINGDBDIR/external/neo4j && tar -xvf neo4j-4.3.23.tar.gz
```
Herein, `$NEO4JDIR = $TURINGDBDIR/external/neo4j/neo4j-community-4.3.23-SNAPSHOT`, i.e. the directory which Neo4j was just extracted into.

 ⚠️ If  ou are using the new GitHub TuringDB repo, you will need to install and pull on `git lfs` to get the real `tar` file. Please do this before running the `setup.sh`.

2. Get fresh Reactome into Neo4j
> Optional: if you already have a working Reactome instance, then use that one. Make sure any references to the graph name are changed, e.g. setting the default graph to the one you will work with.
```
cd $NEO4JDIR/data/databases
rm -rf graph.db
wget https://reactome.org/download/current/reactome.graphdb.tgz
tar -xzvf reactome.graphdb.tgz
```
I needed to remove the old `graph.db` and replace it with the new one, which the `tar` extraction provides.

3. Configure Neo4j: set the default graph to your working Reactome
```
echo "dbms.default_database=graph.db" >> $NEO4JDIR/conf/neo4j.conf

echo "dbms.recovery.fail_on_missing_files=false" >> $NEO4JDIR/conf/neo4j.conf

echo "unsupported.dbms.tx_log.fail_on_corrupted_log_files=false" >> $NEO4JDIR/conf/neo4j.conf

echo "dbms.security.auth_enabled=false" >> $NEO4JDIR/conf/neo4j.conf
```

4. Start the Neo4j instance
```
cd $NEO4JDIR
bin/neo4j start
```
> Note the address which the server is running on, you may need to supply this as an argument to the benchmarking script

⚠️ There is an error which I ran into where the first time you start Neo4j the database will be offline. It is fixed by stopping Neo4j and restarting it:

```
cd $NEO4JDIR
bin/neo4j stop
bin/neo4j start
```
NOTE: The setup script attempts to restart Neo4j to fix this, but it is temperamental, please try restarting Neo4j yourself after running `setup.sh` if the DB is still offline.

5. Create and build the Python virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

6. Run the benchmark script, example usage:
```
python3 bench.py --query "samples/neo4j-str-prop-multihop.cypher" --runs 3
```
