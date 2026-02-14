#!/usr/bin/env python3
"""Generate a comprehensive benchmark report from individual dataset reports."""

import argparse
import datetime
import importlib.metadata
import logging
import re
import statistics
import subprocess
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import Any, Dict, List

from report_summary.parse_benchmark_report import BenchmarkReportParser

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Query categories in priority order. First match wins.
# Each entry: (category_name, classifier_function)
CATEGORY_RULES: list[tuple[str, Callable[[str], bool]]] = []


def _count_hops(query: str) -> int:
    """Count the number of --> chains in a query."""
    return len(re.findall(r"-->[^-]", query)) + len(re.findall(r"-->$", query))


def _has_property_filter(query: str) -> bool:
    """Check if query has inline property filter {prop: val} or WHERE ... = ."""
    return bool(
        re.search(r"\{[^}]+\}", query) or re.search(r"WHERE\s+\S+\s*[=<>!]", query)
    )


def _has_label(query: str) -> bool:
    """Check if query has a node label like (n:Label)."""
    return bool(re.search(r"\(\w*:\w+", query))


def _has_rel_type(query: str) -> bool:
    """Check if query has a relationship type like [:TYPE]."""
    return bool(re.search(r"\[[\w]*:[\w]+\]", query))


def _has_aggregation(query: str) -> bool:
    """Check if query returns an aggregation like count(...)."""
    return bool(re.search(r"RETURN\s+.*\bcount\s*\(", query, re.IGNORECASE))


def _is_full_graph_scan(query: str) -> bool:
    """Check if query is MATCH (n) RETURN or MATCH ()-[r]->() RETURN with no filters."""
    # Node scan: MATCH (n) RETURN n
    if re.match(
        r"MATCH\s+\(\w+\)\s+RETURN\s+", query, re.IGNORECASE
    ) and not _has_label(query):
        return True
    # Edge scan: MATCH ()-[r]->() RETURN r
    if re.match(
        r"MATCH\s+\(\s*\)\s*-\[\w+\]->\s*\(\s*\)\s+RETURN\s+", query, re.IGNORECASE
    ) and not _has_rel_type(query):
        return True
    return False


def _is_label_scan(query: str) -> bool:
    """Label scan: has label, no relationship traversal, no property filter."""
    if not _has_label(query):
        return False
    if _has_property_filter(query):
        return False
    if "-->" in query or "<--" in query or re.search(r"-\[[\w:]*\]->", query):
        return False
    return True


def _is_aggregation(query: str) -> bool:
    return _has_aggregation(query)


def _is_multi_hop(query: str) -> bool:
    """Multi-hop: 2+ --> chains with a property filter anchor node."""
    return _count_hops(query) >= 2 and _has_property_filter(query)


def _is_property_filter(query: str) -> bool:
    """Property filter: has property filter, at most one hop, no typed relationship."""
    if not _has_property_filter(query):
        return False
    if _count_hops(query) > 1:
        return False
    return True


def _is_rel_type_traversal(query: str) -> bool:
    """Relationship type traversal: has [:TYPE] edge pattern."""
    return _has_rel_type(query)


# Build category rules in priority order
CATEGORY_RULES = [
    ("Aggregations", _is_aggregation),
    ("Full Graph Scans", _is_full_graph_scan),
    ("Label Scans", _is_label_scan),
    ("Multi-Hop Traversals", _is_multi_hop),
    ("Property-Based Filtering", _is_property_filter),
    ("Relationship Type Traversal", _is_rel_type_traversal),
    ("Complex Patterns", lambda _q: True),  # catch-all
]

# Map category names to template section numbers
CATEGORY_SECTION_MAP = {
    "Label Scans": "5.1",
    "Full Graph Scans": "5.2",
    "Property-Based Filtering": "5.3",
    "Relationship Type Traversal": "5.4",
    "Multi-Hop Traversals": "5.5",
    "Complex Patterns": "5.6",
    "Aggregations": "5.7",
}


def classify_query(query: str) -> str:
    """Return the category name for a query using ordered rules."""
    for name, func in CATEGORY_RULES:
        if func(query):
            return name
    return "Complex Patterns"


class ReportGenerator:
    def __init__(self, reports_dir: Path, template_path: Path):
        self.reports_dir = reports_dir
        self.template_path = template_path
        self.parsers: Dict[str, BenchmarkReportParser] = {}
        self.summaries: Dict[str, List[Dict[str, str]]] = {}

    def _discover_reports(self) -> Dict[str, Path]:
        """Find {dataset}_benchmark_report.txt files in reports_dir."""
        reports = {}
        for path in sorted(self.reports_dir.glob("*_benchmark_report.txt")):
            dataset = path.stem.replace("_benchmark_report", "")
            reports[dataset] = path
        if not reports:
            logger.warning(f"No benchmark reports found in {self.reports_dir}")
        else:
            logger.info(f"Found reports for: {', '.join(reports)}")
        return reports

    def _parse_all(self) -> None:
        """Parse all discovered reports and create summaries."""
        report_files = self._discover_reports()
        for dataset, path in report_files.items():
            try:
                parser = BenchmarkReportParser(str(path))
                parser.parse()
                summary = parser.create_summary()
                if summary:
                    self.parsers[dataset] = parser
                    self.summaries[dataset] = summary
                    logger.info(
                        f"Parsed {dataset}: {len(summary)} queries across "
                        f"{len(parser.tools_data)} engines"
                    )
                else:
                    logger.warning(f"No summary data for {dataset}")
            except Exception as e:
                logger.warning(f"Failed to parse {dataset}: {e}")

    def _group_by_category(
        self, summary: List[Dict[str, str]]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Group summary rows by query category."""
        groups: Dict[str, List[Dict[str, str]]] = {}
        for row in summary:
            category = classify_query(row["Query"])
            groups.setdefault(category, []).append(row)
        return groups

    def _compute_aggregate_stats(self) -> Dict[str, Any]:
        """Compute aggregate speedup stats across all datasets."""
        neo4j_speedups: list[float] = []
        memgraph_speedups: list[float] = []

        for summary in self.summaries.values():
            for row in summary:
                for col, target in [
                    ("Speedup vs Neo4j", neo4j_speedups),
                    ("Speedup vs Memgraph", memgraph_speedups),
                ]:
                    val = row.get(col, "-")
                    match = re.match(r"([\d.]+)x", val)
                    if match:
                        target.append(float(match.group(1)))

        def _stats(values: list[float]) -> Dict[str, Any]:
            if not values:
                return {
                    "avg": 0,
                    "median": 0,
                    "min": 0,
                    "max": 0,
                    "wins": 0,
                    "losses": 0,
                    "total": 0,
                }
            return {
                "avg": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "wins": sum(1 for v in values if v >= 1.0),
                "losses": sum(1 for v in values if v < 1.0),
                "total": len(values),
            }

        return {
            "neo4j": _stats(neo4j_speedups),
            "memgraph": _stats(memgraph_speedups),
            "total_queries": sum(len(s) for s in self.summaries.values()),
            "total_datasets": len(self.summaries),
        }

    def _find_competitor_wins(self) -> List[Dict[str, str]]:
        """Find queries where a competitor is faster (speedup < 1.0)."""
        losses = []
        for dataset, summary in self.summaries.items():
            for row in summary:
                for col in ("Speedup vs Neo4j", "Speedup vs Memgraph"):
                    val = row.get(col, "-")
                    match = re.match(r"([\d.]+)x", val)
                    if match and float(match.group(1)) < 1.0:
                        competitor = col.replace("Speedup vs ", "")
                        losses.append(
                            {
                                "dataset": dataset,
                                "query": row["Query"],
                                "competitor": competitor,
                                "speedup": val,
                                "turing_time": row.get("TuringDB", "-"),
                                "competitor_time": row.get(competitor, "-"),
                            }
                        )
        return losses

    def _build_hardware_table(self) -> str:
        """Build hardware specs table using machine info."""
        specs = _collect_machine_specs()
        lines = [
            "| Spec     | Value                    |",
            "|----------|--------------------------|",
        ]
        for key, value in specs.items():
            lines.append(f"| {key:<8} | {value:<24} |")
        return "\n".join(lines)

    def _build_software_versions(self) -> str:
        """Build software versions tables for engines and client tools."""
        all_versions = _collect_software_versions()
        engines = all_versions["engines"]
        clients = all_versions["clients"]

        lines = [
            "**Database Engines**",
            "",
            "| Database  | Version                 |",
            "|-----------|-------------------------|",
        ]
        for name, version in engines.items():
            lines.append(f"| {name:<9} | {version:<23} |")

        lines.append("")
        lines.append("**Client & Tools**")
        lines.append("")
        lines.append("| Component              | Version                 |")
        lines.append("|------------------------|-------------------------|")
        for name, version in clients.items():
            lines.append(f"| {name:<22} | {version:<23} |")

        return "\n".join(lines)

    def _build_markdown_table(self, rows: List[Dict[str, str]]) -> str:
        """Build a markdown table from summary rows."""
        if not rows:
            return "*No queries in this category.*\n"

        columns = [
            "TuringDB",
            "Neo4j",
            "Memgraph",
            "Speedup vs Neo4j",
            "Speedup vs Memgraph",
        ]
        # Only include columns that exist in the data
        columns = [c for c in columns if any(c in row for row in rows)]

        lines = []
        lines.append("| Query | " + " | ".join(columns) + " |")
        lines.append("|" + "|".join(["-------"] + ["------" for _ in columns]) + "|")
        for row in rows:
            query = f"`{row['Query']}`"
            values = " | ".join(row.get(col, "-") for col in columns)
            lines.append(f"| {query} | {values} |")
        return "\n".join(lines)

    def _build_dataset_section(self, dataset: str) -> str:
        """Build results tables for a single dataset."""
        summary = self.summaries[dataset]
        lines = [f"### {dataset.capitalize()}\n"]
        lines.append(self._build_markdown_table(summary))
        lines.append("")
        return "\n".join(lines)

    def _build_results_overview(self) -> str:
        """Build the combined results overview across all datasets."""
        sections = []
        for dataset in sorted(self.summaries):
            sections.append(self._build_dataset_section(dataset))
        return "\n".join(sections)

    def _build_results_by_category(self) -> str:
        """Build per-category results with tables, preserving narrative text."""
        # Collect all queries across all datasets, grouped by category
        all_by_category: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
        for dataset in sorted(self.summaries):
            groups = self._group_by_category(self.summaries[dataset])
            for category, rows in groups.items():
                all_by_category.setdefault(category, {})[dataset] = rows

        # Build sections in the template's order
        ordered_categories = [
            "Label Scans",
            "Full Graph Scans",
            "Property-Based Filtering",
            "Relationship Type Traversal",
            "Multi-Hop Traversals",
            "Complex Patterns",
            "Aggregations",
        ]

        sections = []
        for category in ordered_categories:
            section_num = CATEGORY_SECTION_MAP[category]
            datasets_data = all_by_category.get(category, {})

            if not datasets_data:
                continue

            section_lines = [f"### {section_num} {category}\n"]

            for dataset in sorted(datasets_data):
                rows = datasets_data[dataset]
                section_lines.append(f"**{dataset.capitalize()}:**\n")
                section_lines.append(self._build_markdown_table(rows))
                section_lines.append("")

            sections.append("\n".join(section_lines))

        return "\n".join(sections)

    def _build_executive_summary(self, stats: Dict[str, Any]) -> str:
        """Build the executive summary key findings."""
        neo4j = stats["neo4j"]
        memgraph = stats["memgraph"]
        total = stats["total_queries"]
        n_datasets = stats["total_datasets"]

        lines = []
        lines.append(f"- Across **{n_datasets} dataset(s)** and **{total} queries**:")

        if neo4j["total"] > 0:
            lines.append(
                f"- TuringDB is **{neo4j['avg']:.1f}x faster** than Neo4j on average "
                f"(median {neo4j['median']:.1f}x, max {neo4j['max']:.0f}x)"
            )
            lines.append(
                f"- TuringDB wins on **{neo4j['wins']}/{neo4j['total']}** queries vs Neo4j"
            )

        if memgraph["total"] > 0:
            lines.append(
                f"- TuringDB is **{memgraph['avg']:.1f}x faster** than Memgraph on average "
                f"(median {memgraph['median']:.1f}x, max {memgraph['max']:.0f}x)"
            )
            lines.append(
                f"- TuringDB wins on **{memgraph['wins']}/{memgraph['total']}** queries vs Memgraph"
            )

        return "\n".join(lines)

    def _build_competitor_wins(self, losses: List[Dict[str, str]]) -> str:
        """Build the section listing queries where competitors win."""
        if not losses:
            return "No queries where competitors outperform TuringDB were found in the benchmark.\n"

        lines = []
        total_queries = sum(len(s) for s in self.summaries.values())
        # Count unique (dataset, query) pairs
        unique_losses = {(loss["dataset"], loss["query"]) for loss in losses}
        pct = len(unique_losses) / total_queries * 100 if total_queries else 0

        lines.append(
            f"The following **{len(unique_losses)} queries** ({pct:.0f}% of benchmark) "
            f"show a competitor outperforming TuringDB:\n"
        )
        lines.append(
            "| Dataset | Query | Competitor | TuringDB | Competitor Time | Speedup |"
        )
        lines.append(
            "|---------|-------|------------|----------|-----------------|---------|"
        )
        for loss in losses:
            lines.append(
                f"| {loss['dataset']} | `{loss['query']}` | {loss['competitor']} "
                f"| {loss['turing_time']} | {loss['competitor_time']} | {loss['speedup']} |"
            )
        lines.append("")
        return "\n".join(lines)

    def _build_appendix_queries(self) -> str:
        """Build appendix listing all queries per dataset, grouped by category."""
        lines = ["<details>", "<summary>Click to expand</summary>", ""]

        for dataset in sorted(self.summaries):
            lines.append(f"### {dataset.capitalize()}\n")
            groups = self._group_by_category(self.summaries[dataset])

            for category in [
                "Full Graph Scans",
                "Label Scans",
                "Property-Based Filtering",
                "Aggregations",
                "Multi-Hop Traversals",
                "Relationship Type Traversal",
                "Complex Patterns",
            ]:
                rows = groups.get(category, [])
                if not rows:
                    continue
                lines.append(f"#### {category}")
                lines.append("```cypher")
                for row in rows:
                    lines.append(row["Query"])
                lines.append("```")
                lines.append("")

        lines.append("</details>")
        return "\n".join(lines)

    def _replace_section(self, content: str, marker: str, replacement: str) -> str:
        """Replace content between <!-- MARKER --> and <!-- /MARKER --> tags."""
        pattern = f"(<!-- {marker} -->).*?(<!-- /{marker} -->)"
        new_content = f"<!-- {marker} -->\n{replacement}\n<!-- /{marker} -->"
        result, count = re.subn(pattern, new_content, content, flags=re.DOTALL)
        if count == 0:
            logger.warning(f"Marker <!-- {marker} --> not found in template")
        return result

    def generate(self) -> str:
        """Main method: parse reports, fill template, return final markdown."""
        self._parse_all()

        if not self.summaries:
            logger.error("No valid benchmark data found. Cannot generate report.")
            return ""

        content = self.template_path.read_text()

        # Set date
        content = content.replace("YYYY-MM-DD", datetime.date.today().isoformat())

        # Compute aggregate stats
        stats = self._compute_aggregate_stats()
        losses = self._find_competitor_wins()

        # Replace data sections
        content = self._replace_section(
            content, "EXECUTIVE_SUMMARY", self._build_executive_summary(stats)
        )
        content = self._replace_section(
            content, "HARDWARE_TABLE", self._build_hardware_table()
        )
        content = self._replace_section(
            content, "SOFTWARE_VERSIONS", self._build_software_versions()
        )
        content = self._replace_section(
            content, "RESULTS_OVERVIEW", self._build_results_overview()
        )
        content = self._replace_section(
            content, "RESULTS_BY_CATEGORY", self._build_results_by_category()
        )
        content = self._replace_section(
            content, "COMPETITOR_WINS", self._build_competitor_wins(losses)
        )
        content = self._replace_section(
            content, "APPENDIX_QUERIES", self._build_appendix_queries()
        )

        return content

    def save(self, output_path: Path) -> None:
        """Generate and write report to file."""
        content = self.generate()
        if not content:
            return
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        logger.info(f"Report saved to {output_path}")


def _collect_machine_specs() -> Dict[str, str]:
    """Collect machine hardware specs."""
    import os
    import platform

    specs: Dict[str, str] = {}

    # CPU
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    specs["CPU"] = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass

    # Cores
    try:
        cores = os.cpu_count()
        if cores:
            specs["Cores"] = str(cores)
    except Exception:
        pass

    # RAM
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    gb = round(kb / 1024 / 1024, 1)
                    specs["RAM"] = f"{gb} GB"
                    break
    except OSError:
        pass

    # Storage
    try:
        result = subprocess.run(
            ["lsblk", "-d", "-o", "NAME,ROTA", "--noheadings"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) == 2:
                specs["Storage"] = "HDD" if parts[1] == "1" else "SSD"
                break
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # OS
    try:
        result = subprocess.run(
            ["lsb_release", "-ds"], capture_output=True, text=True, check=True
        )
        specs["OS"] = result.stdout.strip().strip('"')
    except (subprocess.CalledProcessError, FileNotFoundError):
        specs["OS"] = f"{platform.system()} {platform.release()}"

    return specs


def _collect_software_versions() -> Dict[str, Dict[str, str]]:
    """Detect installed versions of database engines, SDKs, and tools."""
    engines: Dict[str, str] = {}
    clients: Dict[str, str] = {}

    # --- Database engines ---

    # TuringDB engine: via CLI
    try:
        result = subprocess.run(
            ["uv", "run", "turingdb", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = (result.stdout + result.stderr).strip()
        match = re.search(r"([\d.]+)", output)
        engines["TuringDB"] = match.group(1) if match else output or "unknown"
    except FileNotFoundError:
        engines["TuringDB"] = "unknown"

    # Neo4j: parse version from pom.xml (neo4j-admin --version needs Java 17+)
    try:
        pom_path = Path("install/neo4j/pom.xml")
        if pom_path.exists():
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            version_el = root.find("m:version", ns)
            if version_el is None:
                version_el = root.find("version")
            if version_el is not None and version_el.text:
                engines["Neo4j"] = version_el.text
            else:
                engines["Neo4j"] = "unknown"
        else:
            engines["Neo4j"] = "unknown"
    except ET.ParseError:
        engines["Neo4j"] = "unknown"

    # Memgraph: from binary --version flag
    try:
        memgraph_bin = Path("install/memgraph/usr/lib/memgraph/memgraph")
        result = subprocess.run(
            [str(memgraph_bin), "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout + result.stderr
        match = re.search(r"memgraph version ([\d.]+)", output, re.IGNORECASE)
        engines["Memgraph"] = match.group(1) if match else "unknown"
    except FileNotFoundError:
        engines["Memgraph"] = "unknown"

    # --- Client SDKs & tools ---

    # Python version
    try:
        result = subprocess.run(
            ["python3", "--version"], capture_output=True, text=True, check=False
        )
        match = re.search(r"([\d.]+)", result.stdout)
        clients["Python"] = match.group(1) if match else "unknown"
    except FileNotFoundError:
        clients["Python"] = "unknown"

    # turingdb Python SDK
    try:
        clients["turingdb (Python SDK)"] = importlib.metadata.version("turingdb")
    except importlib.metadata.PackageNotFoundError:
        clients["turingdb (Python SDK)"] = "unknown"

    # neo4j Python driver (used for both Neo4j and Memgraph)
    try:
        clients["neo4j (Python driver)"] = importlib.metadata.version("neo4j")
    except importlib.metadata.PackageNotFoundError:
        clients["neo4j (Python driver)"] = "unknown"

    # mgconsole
    try:
        mgconsole_bin = Path("install/memgraph/usr/bin/mgconsole")
        result = subprocess.run(
            [str(mgconsole_bin), "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        match = re.search(r"([\d.]+)", result.stdout)
        clients["mgconsole"] = match.group(1) if match else "unknown"
    except FileNotFoundError:
        clients["mgconsole"] = "unknown"

    return {"engines": engines, "clients": clients}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate comprehensive benchmark report from individual dataset reports"
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Directory containing {dataset}_benchmark_report.txt files (default: reports/)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("report_summary/BENCHMARK_REPORT_TEMPLATE.md"),
        help="Path to template file (default: report_summary/BENCHMARK_REPORT_TEMPLATE.md)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("reports/benchmark_report.md"),
        help="Output file path (default: reports/benchmark_report.md)",
    )
    args = parser.parse_args()

    if not args.template.exists():
        logger.error(f"Template file not found: {args.template}")
        return

    generator = ReportGenerator(args.reports_dir, args.template)
    generator.save(args.output)


if __name__ == "__main__":
    main()
