#!/usr/bin/env python3

import argparse
import sys
import time
from dataclasses import dataclass, field
from neo4j import READ_ACCESS, GraphDatabase
from typing import List, Dict, Tuple
from tabulate import tabulate

from neo4j._work import Query

@dataclass
class BenchmarkResult:
    query_times: Dict[str, List[int]] = field(default_factory=dict)
    query_sizes: Dict[str, int] = field(default_factory=dict)

def run_queries(queries : list[str], driver, db="graph.db", runs : int =1) -> BenchmarkResult:
    res = BenchmarkResult()

    for query in queries:
      print(f"Running benchmarks for: {query}")

      for run in range(1, runs+1):
        print(f"\rRun {run}/{runs}", end='', flush=True)

        query_timer = time.perf_counter_ns()
        result = [dict(r) for r in driver.session().run(query)]
        res.query_times.setdefault(query, []).append((time.perf_counter_ns() - query_timer) // 1_000)  # microseconds
        if (query not in res.query_sizes):
          res.query_sizes[query] =  len(result)

      print()

    return res

def present_results(results: BenchmarkResult, runs: int) -> None:
    table = []
    headers = [
        "Query",
        "Mean",
        "Min",
        "Max",
        "Median",
        "Throughput (queries/second)",
        "Result size"
    ]
    table.append(headers)

    for query, times in results.query_times.items():
        times.sort()
        n: int = runs
        _sum: int = sum(times)

        mean = _sum // n
        min_ = times[0]
        max_ = times[-1]
        median = (times[n // 2 - 1] + times[n // 2]) // 2 if (n % 2 == 0) else times[n // 2]
        throughput = n / ((_sum / 1_000) / 1_000)  # n / total_seconds

        ms = lambda us: f"{us // 1_000}ms"

        table.append([
            query,
            ms(mean),
            ms(min_),
            ms(max_),
            ms(median),
            f"{throughput:.6f}",
            f"{results.query_sizes.get(query, '?')}"
        ])

    print(tabulate(table, tablefmt="grid"))


def main() -> None:
    parser = argparse.ArgumentParser(description='Neo4j Benchmarking Tool')
    parser.add_argument('--url', '-u', default='bolt://localhost:7687',
                       help='Neo4j connection URL (default: bolt://localhost:7687)')
    parser.add_argument('--username', '-n', default='neo4j',
                       help='Username (default: neo4j)')
    parser.add_argument('--password', '-p', default='neo4j',
                       help='Password (default: neo4j)')
    parser.add_argument('--database', '-g', default='graph.db',
                       help='Default database (default: neo4j)')
    parser.add_argument('--query', '-q',
                       help="The query file to run against the loaded DB.")
    parser.add_argument('--debug', '-d', default=False,
                       help="Enable debug mode: logs errors of queries.")
    parser.add_argument('--runs', '-r', default=1,
                       help="The number of runs per benchmark")
    
    args = parser.parse_args()

    # Create driver
    try:
        driver = GraphDatabase.driver(args.url, auth=(args.username, args.password))
        print(f"Connected to {args.url}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

      # q = lambda query, db=args.database: [dict(r) for r in driver.session(database=db).run(query)]
    queries = [line.strip().split(';')[0] for line in open(args.query) if line.strip()]

    res : BenchmarkResult = run_queries(queries, driver, args.database, int(args.runs))
    print("Closed Neo4j session")
    present_results(res, int(args.runs))
    

if __name__ == "__main__":
  main()
