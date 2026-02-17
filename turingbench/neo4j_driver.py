#!/usr/bin/env python3

import sys
import argparse
from typing import List, Dict, Any, LiteralString, cast

from .abstract_driver import AbstractDriver
from .memory_sampler import find_server_pid

from neo4j import GraphDatabase


class Neo4jDriver(AbstractDriver):
    """Neo4j-specific implementation of DatabaseBenchmark"""

    def connect(
        self, url: str, username: str, password: str, database: str = "neo4j"
    ) -> None:
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(url, auth=(username, password))
            self.database = database
            print(f"Connected to {url}")
        except Exception as e:
            print(f"Failed to connect: {e}")
            sys.exit(1)

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a Neo4j query and return results"""
        with self.driver.session(database=self.database) as session:
            return [dict(r) for r in session.run(cast(LiteralString, query))]

    def close(self) -> None:
        """Close the Neo4j driver"""
        if hasattr(self, "driver") and self.driver:
            self.driver.close()
            print("Closed Neo4j connection")

    @classmethod
    def add_db_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """Add Neo4j-specific arguments"""
        parser.add_argument(
            "--url",
            "-u",
            default="bolt://localhost:7687",
            help="Neo4j connection URL (default: bolt://localhost:7687)",
        )
        parser.add_argument(
            "--username", "-n", default="neo4j", help="Username (default: neo4j)"
        )
        parser.add_argument(
            "--password", "-p", default="neo4j", help="Password (default: neo4j)"
        )
        parser.add_argument(
            "--database", "-g", default="neo4j", help="Database name (default: neo4j)"
        )


def main(args: argparse.Namespace, engine: str = "neo4j") -> None:
    driver = Neo4jDriver()

    try:
        driver.connect(
            url=args.url,
            username=args.username,
            password=args.password,
            database=args.database,
        )
        driver.server_pid = find_server_pid(engine)

        # Load queries from file
        with open(args.query, "r") as f:
            queries = [line.strip().split(";")[0] for line in f if line.strip()]

        # Run benchmark
        driver.run_benchmark(queries, args.runs)

    finally:
        driver.close()


if __name__ == "__main__":
    parser = Neo4jDriver.create_argument_parser(description="Neo4j Benchmarking Tool")
    args = parser.parse_args()

    main(args)
