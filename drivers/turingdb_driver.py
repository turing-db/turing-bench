#!/usr/bin/env python3

import sys
import argparse
import pandas as pd
from typing import List, Dict, Any, cast

from abstract_driver import AbstractDriver

from turingdb import TuringDB

class TuringDBDriver(AbstractDriver):
  _default_url : str = 'http://localhost:6666'
  _default_db : str = 'default'

  def connect(self, url: str, database: str = "default") -> None:
    try:
      self.client = TuringDB(host=url)
    except Exception as e:
      print(f"Failed to connect to TuringDB: {e}")
      sys.exit(-1)
      
    try:
      loaded_graphs = self.client.list_loaded_graphs()
      if database not in loaded_graphs:
        self.client.load_graph(graph_name=database, raise_if_loaded=False)
    except Exception as e:
      print(f"Failed to load graph: {e}")
      sys.exit(-1)

    try:
      self.client.set_graph(graph_name=database)
    except Exception as e:
      print(f"Failed to use graph: {e}")
      sys.exit(-1)

  def close(self) -> None:
    # TODO: Shutdown TuringDB
    ...

  
  def execute_query(self, query: str) -> List[Dict[str, Any]]:
    df = self.client.query(query)
    return cast(List[Dict[str, Any]], df.to_dict('records'))

  @classmethod
  def add_db_arguments(cls, parser: argparse.ArgumentParser) -> None:
      parser.add_argument('--url', '-u', default=cls._default_url,
                         help=f'Neo4j connection URL (default: {cls._default_url}')

      parser.add_argument('--database', '-g', default=cls._default_db,
                   help=f'Database name (default: {cls._default_db})')

def main() -> None:
  parser = TuringDBDriver.create_argument_parser(description="TuringDB Benchmarking Tool")
  args = parser.parse_args()

  driver = TuringDBDriver()

  try:
    driver.connect(
      url=args.url,
      database=args.database
    )

    # Load queries from file
    with open(args.query, 'r') as f:
        queries = [line.strip().split(';')[0] for line in f if line.strip()]

    driver.run_benchmark(queries, args.runs)

  finally:
    driver.close()

if __name__ == "__main__":
  main()
