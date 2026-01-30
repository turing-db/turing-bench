# Benchmark Results
This branch contains the **nightly benchmark results** for TuringDB. It is **automatically maintained by CI** and should not be modified manually.

## Overview

- Each benchmark run is generated nightly (or on workflow dispatch).  
- The `results` branch only contains:
  - `README.md`  
  - `results/` folders with benchmark outputs and metadata
- Humans should **never push directly** to this branch; only the CI workflow writes here.

## Branch Structure
All benchmark results are stored under the `results/` folder, organized by **date** and **time**:
..

## Purpose

This branch provides a historical record of benchmark results.
It is intended for:
- Tracking performance over time
- Running statistics or aggregating results

