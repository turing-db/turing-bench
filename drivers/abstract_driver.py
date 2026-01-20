#!/usr/bin/env python3

import argparse
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any
from tabulate import tabulate


@dataclass
class BenchmarkResult:
    query_times: Dict[str, List[int]] = field(default_factory=dict)
    query_sizes: Dict[str, int] = field(default_factory=dict)


class AbstractDriver(ABC):
    """Abstract base class for database benchmarking"""
    
    def __init__(self):
        self.connection = None
    
    @abstractmethod
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a single query and return results as a list of dictionaries.
        Implement this to handle database-specific query execution.
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        # No matter which database we are testing, all the drivers need these args
        Close the database connection.
        Implement this to handle database-specific cleanup.
        """
        pass
    
    def run_queries(self, queries: List[str], runs: int = 1) -> BenchmarkResult:
        """
        Run benchmark queries multiple times and collect timing data.
        This method is generic and doesn't need to be overridden.
        """
        res = BenchmarkResult()
        
        for query in queries:
            print(f"Running benchmarks for: {query}")
            for run in range(1, runs + 1):
                print(f"\rRun {run}/{runs}", end='', flush=True)
                
                query_timer = time.perf_counter_ns()
                result = self.execute_query(query)
                elapsed_us = (time.perf_counter_ns() - query_timer) // 1_000  # microseconds
                
                res.query_times.setdefault(query, []).append(elapsed_us)
                
                if query not in res.query_sizes:
                    res.query_sizes[query] = len(result)
            print()
        
        return res
    
    def present_results(self, results: BenchmarkResult, runs: int) -> None:
        """
        Present benchmark results in a formatted table.
        This method is generic and doesn't need to be overridden.
        """
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
        
        for query, times in results.query_times.items():
            times_sorted = sorted(times)
            n = runs
            sum_ = sum(times_sorted)
            mean = sum_ // n
            min_ = times_sorted[0]
            max_ = times_sorted[-1]
            median = (times_sorted[n // 2 - 1] + times_sorted[n // 2]) // 2 if (n % 2 == 0) else times_sorted[n // 2]
            throughput = n / ((sum_ / 1_000_000))  # n / total_seconds
            
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
        
        print(tabulate(table, headers=headers, tablefmt="grid"))
    
    # DB-specific arguments (e.g. Neo4j password, etc.)
    @classmethod
    def add_db_arguments(cls, parser: argparse.ArgumentParser) -> None:
        """
        Add database-specific arguments to the argument parser.
        Override this to add custom arguments for your database.
        """
        pass

    # No matter which database we are testing, all the drivers need these args
    @staticmethod
    def add_common_arguments(parser: argparse.ArgumentParser) -> None:
        """Add common arguments for all database benchmarks"""
        parser.add_argument('--query', '-q', required=True,
                           help="The query file to run against the database")
        parser.add_argument('--debug', '-d', action='store_true',
                           help="Enable debug mode: logs errors of queries")
        parser.add_argument('--runs', '-r', type=int, default=1,
                           help="The number of runs per benchmark")

    # Combines derived db-specific and common arguments into a single argparser
    @classmethod
    def create_argument_parser(cls, description: str = "Database Benchmarking Tool") -> argparse.ArgumentParser:
        """
        Create and configure argument parser with common and database-specific arguments.
        This is a convenience method that combines common and database-specific arguments.
        """
        parser = argparse.ArgumentParser(description=description)
        cls.add_common_arguments(parser)
        cls.add_db_arguments(parser)
        return parser

    def run_benchmark(self, queries: List[str], runs: int) -> None:
        """
        Main benchmark orchestration method.
        This method is generic and doesn't need to be overridden.
        """
        results = self.run_queries(queries, runs)
        print("Benchmark completed")
        self.present_results(results, runs)
