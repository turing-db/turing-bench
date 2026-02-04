script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
install_dir="$script_dir/install"
export JAVA_HOME="$install_dir/java/jdk-17.0.12"
export JDK_HOME="$install_dir/java/jdk-17.0.12"
export JRE_HOME="$install_dir/java/jdk-17.0.12"
export NEO4J_HOME="$install_dir/neo4j-build"
export NEO4J_IMPORT="$NEO4J_HOME/import"
export NEO4J_DATA_DIR="$NEO4J_HOME/data"
export MEMGRAPH_HOME="$install_dir/memgraph"
export TURINGDB_DIR="$install_dir/turingdb"
export TURINGDB_DATA_DIR="$TURINGDB_DIR/data"
export TURINGDB_GRAPHS_DIR="$TURINGDB_DIR/graphs"
export SCRIPTS="$script_dir/scripts"
export DUMPS="$script_dir/dumps"
export QUERIES_DIR="$script_dir/sample_queries"
export PATH=$PATH:"$install_dir/java/jdk-17.0.12/bin"
export PATH=$PATH:"$install_dir/maven/apache-maven-3.9.12/bin"
export PATH=$PATH:"$NEO4J_HOME/bin"

alias memgraph="$install_dir/memgraph/usr/lib/memgraph/memgraph"
alias mgconsole="$install_dir/memgraph/usr/bin/mgconsole"
alias bench="uv run $SCRIPTS/manage_servers.py"

function elapsed() {
    local end=`date +%s`
    runtime=$((end-start))
    echo "$runtime sec"
}
