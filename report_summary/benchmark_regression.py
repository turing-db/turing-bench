#!/usr/bin/env python3
"""
Compute a 7-day median baseline for TuringDB runtimes from historical compiled
markdown reports and return per-dataset per-query delta percentages.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Optional

logger = logging.getLogger(__name__)

# Minimum number of historical report files required to run at all
MIN_REPORTS = 5
# Maximum number of historical report files to use (newest-first)
MAX_REPORTS = 7
# Minimum number of data points for a specific query before computing its delta.
# Lower than MIN_REPORTS to handle queries recently added to the benchmark.
MIN_QUERY_DATAPOINTS = 5


def _parse_report_date(path: Path) -> Optional[datetime]:
    """
    Extract the datetime from a report filename.
    Expected pattern: benchmark_report_<dataset>_YYYY-MM-DD_HH-MM-SS.md
    """
    match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", path.name)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S")
    return None


def _parse_ms(value: str) -> Optional[float]:
    """Parse '5ms' or '1265ms' into a float, or None if unparsable."""
    match = re.match(r"(\d+(?:\.\d+)?)\s*ms", value.strip())
    return float(match.group(1)) if match else None


def _format_delta(pct: float) -> str:
    """Format a percentage delta, e.g. '+8.3%' or '-2.1%'."""
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def _find_historical_reports(current: Path) -> list[Path]:
    """
    Find up to MAX_REPORTS historical compiled .md reports in the same directory
    as the current report, excluding the current report itself, sorted newest-first.
    Only reports strictly older than the current one are included.
    """
    current_date = _parse_report_date(current)

    candidates: list[tuple[datetime, Path]] = []
    for path in current.parent.glob("benchmark_report_*.md"):
        if path.resolve() == current.resolve():
            continue
        dt = _parse_report_date(path)
        if dt is None:
            continue
        if current_date and dt >= current_date:
            continue
        candidates.append((dt, path))

    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = [p for _, p in candidates[:MAX_REPORTS]]

    logger.info(
        f"Found {len(selected)} historical report(s) in {current.parent} "
        f"(need at least {MIN_REPORTS})."
    )
    return selected


def _extract_turingdb_runtimes(report_path: Path) -> dict[str, dict[str, float]]:
    """
    Parse a compiled markdown report and extract TuringDB runtimes per dataset.

    Reads tables within <!-- RESULTS_OVERVIEW --> ... <!-- /RESULTS_OVERVIEW -->
    where each dataset section starts with '### <dataset>'.

    Returns: {dataset: {query: ms}}
    """
    content = report_path.read_text()

    start = content.find("<!-- RESULTS_OVERVIEW -->")
    end = content.find("<!-- /RESULTS_OVERVIEW -->")
    if start == -1 or end == -1:
        logger.warning(f"No RESULTS_OVERVIEW section found in {report_path.name}")
        return {}

    section = content[start:end]
    result: dict[str, dict[str, float]] = {}
    current_dataset: Optional[str] = None
    turingdb_col: Optional[int] = None

    for line in section.splitlines():
        # Dataset subsection header: ### Reactome
        dataset_match = re.match(r"^###\s+(\w+)", line)
        if dataset_match:
            current_dataset = dataset_match.group(1).lower()
            turingdb_col = None
            continue

        if current_dataset is None or "|" not in line:
            continue

        parts = [p.strip() for p in line.split("|")]
        # Ignore empty-bordered split artifacts
        parts = [p for p in parts if p != ""]

        # Detect header row to find TuringDB column index
        if turingdb_col is None:
            lower_parts = [p.lower() for p in parts]
            if "query" in lower_parts and "turingdb" in lower_parts:
                turingdb_col = lower_parts.index("turingdb")
            continue

        # Skip separator rows
        if re.match(r"^[-|: ]+$", line.replace("|", "").replace("-", "").replace(":", "").replace(" ", "") + "x"):
            continue

        if len(parts) <= turingdb_col:
            continue

        # Query is always first column, strip backticks
        query = parts[0].strip("`")
        if not query.lower().startswith(("match", "create")):
            continue

        ms = _parse_ms(parts[turingdb_col])
        if ms is not None:
            result.setdefault(current_dataset, {})[query] = ms

    return result


class BenchmarkRegression:
    """
    Loads historical compiled markdown reports, computes per-query TuringDB
    median runtimes as a baseline, and returns formatted delta strings.
    """

    def __init__(self, current_report: Path):
        self._current = current_report

    def compute(self) -> dict[str, dict[str, str]]:
        """
        Find historical reports, build the baseline, and return delta strings.

        Returns:
            {dataset: {query: delta_str}}
            Returns an empty dict if not enough history is available.
        """
        historical_paths = _find_historical_reports(self._current)

        if len(historical_paths) < MIN_REPORTS:
            logger.warning(
                f"Only {len(historical_paths)} historical report(s) available; "
                f"need at least {MIN_REPORTS}. Skipping baseline."
            )
            return {}

        # Accumulate historical runtimes: {dataset: {query: [ms, ...]}}
        history: dict[str, dict[str, list[float]]] = {}
        for path in historical_paths:
            try:
                runtimes = _extract_turingdb_runtimes(path)
            except Exception as e:
                logger.warning(f"Could not parse {path.name}: {e}")
                continue
            for dataset, query_map in runtimes.items():
                for query, ms in query_map.items():
                    history.setdefault(dataset, {}).setdefault(query, []).append(ms)

        if not history:
            logger.warning("No usable historical data found. Skipping baseline.")
            return {}

        # Load today's TuringDB runtimes from the current report
        today_runtimes = _extract_turingdb_runtimes(self._current)

        deltas: dict[str, dict[str, str]] = {}
        for dataset, query_map in today_runtimes.items():
            for query, today_ms in query_map.items():
                historical_values = history.get(dataset, {}).get(query, [])

                if len(historical_values) < MIN_QUERY_DATAPOINTS:
                    continue

                baseline_ms = median(historical_values)
                if baseline_ms == 0:
                    continue

                pct = ((today_ms - baseline_ms) / baseline_ms) * 100
                deltas.setdefault(dataset, {})[query] = _format_delta(pct)

        logger.info("Baseline deltas computed successfully.")
        return deltas