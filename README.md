# `turing-bench`
> Benchmarking tool for TuringDB. Using the TuringDB C++ SDK.

## Usage
Build as standard Turing Biosystems project, and run `./turing-bench -h` in `build/build_package` to see command line options.

Example usage:

`./turing-bench --load "reactome" --query "samples/str-prop-multihop.cypher" --runs 100 --per-query`

This will run the queries in `samples/str-prop-multihop.cypher` against the `reactome` database, running each query `100` times, and reporting the stats for each individual query.

## Example Query Files
Example query files are provided in `samples/`.
