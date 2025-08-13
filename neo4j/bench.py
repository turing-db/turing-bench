#!/usr/bin/env python3

from neo4j import GraphDatabase
import argparse
import sys

def run_query(query : str, db : str, driver):
  return [dict(r) for r in driver.session(database=db).run(query)]

def main():
    parser = argparse.ArgumentParser(description='Neo4j Query Tool')
    parser.add_argument('--url', '-u', default='bolt://localhost:7474',
                       help='Neo4j connection URL (default: bolt://localhost:7474)')
    parser.add_argument('--username', '-n', default='neo4j',
                       help='Username (default: neo4j)')
    parser.add_argument('--password', '-p', default='neo4j',
                       help='Password (default: neo4j)')
    parser.add_argument('--database', '-d', default='graph.db',
                       help='Default database (default: neo4j)')
    parser.add_argument('--query', '-q',
                       help="The query file to run against the loaded DB.")
    parser.add_argument('--debug', 'd', default=False,
                       help="Enable debug mode: logs errors of queries.")
    parser.add_argument('--runs', '-r', default=1,
                       help="The number of runs per benchmark")
    
    args = parser.parse_args()

    q = lambda query, db=args.database: [dict(r) for r in driver.session(database=db).run(query)]

    # Create driver
    try:
        driver = GraphDatabase.driver(args.url, auth=(args.username, args.password))
        print(f"Connected to {args.url}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    queries = [line.strip().split(';') for line in open(args.query)]
    list(map(queries, print))
