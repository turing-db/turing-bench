#!/usr/bin/env bash

set -e -u -o pipefail
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
install_dir="$script_dir/install"

cd $script_dir
source ./env.sh

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  -h, --help              print this help"
      echo "  --clean                 clean up the environment"
      exit 0
      ;;
    --clean)
      echo "- Cleaning up the environment"
      if [ -d $install_dir ]; then
          rm -rf "$install_dir"
      fi

      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [ ! -d "$install_dir" ]; then
    mkdir "$install_dir"
fi

cd $install_dir

# Download java 17
if [ ! -d "java" ]; then
    echo "- Installing Java 17"
    mkdir java
    cd java
    wget https://download.oracle.com/java/17/archive/jdk-17.0.12_linux-x64_bin.tar.gz
    tar -xf jdk-17.0.12_linux-x64_bin.tar.gz
    rm jdk-17.0.12_linux-x64_bin.tar.gz
else
    echo "- Skipping Java 17 installation: already installed"
fi

cd $install_dir
    
# Download maven
if [ ! -d "maven" ]; then
    echo "- Installing maven"
    mkdir maven
    cd maven
    wget https://dlcdn.apache.org/maven/maven-3/3.9.12/binaries/apache-maven-3.9.12-bin.tar.gz
    tar -xf apache-maven-3.9.12-bin.tar.gz
    rm apache-maven-3.9.12-bin.tar.gz
else
    echo "- Skipping maven installation: already installed"
fi

cd $install_dir
NEO4J_VERSION=5.26.19
NEO4J_BUILD_DIR="$install_dir/neo4j-build"

# Download and install neo4j
if [ ! -d "neo4j" ]; then
    echo "- Downloading neo4j"
    ARCHIVE=neo4j-community-$NEO4J_VERSION-SNAPSHOT-unix.tar.gz
    git clone --depth 1 https://github.com/neo4j/neo4j.git --branch $NEO4J_VERSION
    cd neo4j
    echo "- Installing neo4j"
    mvn clean install -DskipTests -T1C

    mkdir $NEO4J_BUILD_DIR
    cp "./packaging/standalone/target/$ARCHIVE" $NEO4J_BUILD_DIR/
    cd $NEO4J_BUILD_DIR
    tar xzf $ARCHIVE --strip-components=1 
    rm $ARCHIVE

    echo "Fixing neo4j default configuration"
    sed -i 's/#\(server\.directories\.import=import\)/\1/g' $NEO4J_BUILD_DIR/conf/neo4j.conf
    sed -i 's/#\(dbms.security.auth_enabled=false\)/\1/g' $NEO4J_BUILD_DIR/conf/neo4j.conf
    printf "apoc.export.file.enabled=true\n" > $NEO4J_BUILD_DIR/conf/apoc.conf
else
    echo "- Skipping neo4j installation: already installed"
fi

cd $install_dir

# Download and install neo4j apoc procedures
if [ ! -f "$NEO4J_BUILD_DIR/plugins/apoc-$NEO4J_VERSION-core.jar" ]; then
    echo "- Downloading neo4j-apoc"
    wget "https://github.com/neo4j/apoc/releases/download/$NEO4J_VERSION/apoc-$NEO4J_VERSION-core.jar"
    echo "- Installing neo4j-apoc"
    mv "./apoc-$NEO4J_VERSION-core.jar" "$NEO4J_BUILD_DIR/plugins/apoc-$NEO4J_VERSION-core.jar"
else
    echo "- Skipping neo4j-apoc installation: already installed"
fi

cd $install_dir

# Download and install memgraph
if [ ! -d "memgraph" ]; then
    echo "- Downloading memgraph"
    mkdir memgraph
    cd memgraph
    wget https://download.memgraph.com/memgraph/v3.7.2/ubuntu-22.04/memgraph_3.7.2-1_amd64.deb
    echo "- Installing memgraph"
    dpkg-deb -x ./memgraph_3.7.2-1_amd64.deb ./
    rm ./memgraph_3.7.2-1_amd64.deb
    mkdir data logs
else
    echo "- Skipping memgraph installation: already installed"
fi

echo "- Install complete"
