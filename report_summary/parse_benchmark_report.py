#!/usr/bin/env python3
"""Parse benchmark report and create summary table"""

import os
import platform
import re
import sys
import subprocess
import csv
import logging
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class BenchmarkReportParser:
    """Parse benchmark report files and extract mean runtimes"""
    
    TOOL_NAME_MAP = {
        'turingdb': 'TuringDB',
        'neo4j': 'Neo4j',
        'memgraph': 'Memgraph'
    }

    TOOL_DISPLAY_ORDER = ['TuringDB', 'Neo4j', 'Memgraph']
    
    def __init__(self, report_file: str, metric: str = "mean", output_dir: str = None):
        self.report_file = Path(report_file)
        
        # Validate that report file exists
        if not self.report_file.exists():
            raise FileNotFoundError(f"Report file not found: {self.report_file}")
        
        self.content = self.report_file.read_text()
        self.tools_data: Dict[str, Dict[str, str]] = {}
        self.summary: List[Dict[str, str]] = []
        self.metric = metric.lower()
        self.output_dir = Path(output_dir) if output_dir else None
    
    def _get_repo_root(self) -> Path:
        """Get the git repository root"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except subprocess.CalledProcessError:
            # Fallback: search for .git directory
            current = Path.cwd()
            while current != current.parent:
                if (current / ".git").exists():
                    return current
                current = current.parent
            raise RuntimeError("Could not find git repository root")
    
    def _ensure_output_dir(self, dataset_name: str = None) -> Path:
        """Get and create output directory if needed"""
        if self.output_dir:
            output_path = self.output_dir
        else:
            # Default: <git_repo_root>/reports/<dataset>
            repo_root = self._get_repo_root()
            if dataset_name:
                output_path = repo_root / "reports" / dataset_name
            else:
                output_path = repo_root / "reports"
        
        output_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory: {output_path}")
        return output_path
    
    def _extract_tables(self) -> Dict[str, Dict[str, str]]:
        """Extract table content for each tool from both format types"""
        tools = {}
        lines = self.content.split('\n')
        current_tool = None
        table_lines = []
        header_match = None
        in_table = False
        
        for line in lines:
            # Format 1: Unicode box drawing header (║ TuringDB ║)
            header_box_match = re.search(
                r'║ (turingdb|neo4j|memgraph)\s+║',
                line,
                re.IGNORECASE
            )
            if header_box_match:
                self._save_tool_table(tools, current_tool, table_lines, header_match)
                current_tool = self.TOOL_NAME_MAP[header_box_match.group(1).lower()]
                header_match = None
                table_lines = []
                in_table = False
            
            # Format 2: "Running benchmark for 'toolname'"
            tool_match = re.search(
                r"Running benchmark for ['\"]?(turingdb|neo4j|memgraph)['\"]?",
                line,
                re.IGNORECASE
            )
            if tool_match:
                self._save_tool_table(tools, current_tool, table_lines, header_match)
                current_tool = self.TOOL_NAME_MAP[tool_match.group(1).lower()]
                header_match = None
                table_lines = []
                in_table = False
            
            # Detect table header (contains Query and Mean columns)
            if "Query" in line and "Mean" in line and "|" in line:
                header_match = line
                in_table = True
            
            # Collect table rows
            elif in_table and current_tool and ('| match' in line.lower() or '| create' in line.lower()):
                table_lines.append(line)
        
        # Save last tool
        self._save_tool_table(tools, current_tool, table_lines, header_match)
        return tools
    
    def _save_tool_table(self, tools: dict, tool: str, lines: list, header: str) -> None:
        """Helper to save tool table data"""
        if tool and lines and header:
            tools[tool] = {
                "header": header,
                "table": '\n'.join(lines)
            }
    
    def _parse_table(self, table_info: Dict[str, str], metric: str = "mean") -> Dict[str, str]:
        """Parse table content and extract query -> metric mapping"""
        query_metric = {}
        
        # Find column indices from header
        header_parts = [part.strip().lower() for part in table_info["header"].split("|")]
        try:
            query_idx = header_parts.index("query")
            metric_idx = header_parts.index(metric.lower())
        except ValueError:
            logger.warning(f"Could not find required columns in header")
            return query_metric
        
        # Parse table rows
        for line in table_info["table"].split('\n'):
            if not line.strip() or '|' not in line:
                continue
            
            parts = [p.strip() for p in line.split('|')]
            if len(parts) <= metric_idx:
                continue
            
            query = parts[query_idx]
            metric_value = parts[metric_idx]
            
            # Validate query format
            if query and metric_value and query.lower().startswith(('match', 'create')):
                query_metric[query] = metric_value
        
        return query_metric
    
    def parse(self) -> Dict[str, Dict[str, str]]:
        """Parse the entire report and return data for all tools"""
        tables = self._extract_tables()
        for tool, table_info in tables.items():
            self.tools_data[tool] = self._parse_table(table_info, self.metric)
        return self.tools_data
    
    def get_all_queries(self) -> List[str]:
        """Get all unique queries in order of first appearance"""
        queries = []
        seen = set()
        
        for line in self.content.split('\n'):
            if '| match' in line.lower() or '| create' in line.lower():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 1:
                    query = parts[1]
                    if query and query.lower() not in seen:
                        queries.append(query)
                        seen.add(query.lower())
        
        return queries
    
    @staticmethod
    def _parse_ms(value: str) -> float | None:
        """Parse a metric value like '5ms' or '1265ms' into a float, or None if unparseable"""
        match = re.match(r'(\d+(?:\.\d+)?)\s*ms', value.strip())
        if match:
            return float(match.group(1))
        return None

    @staticmethod
    def _format_speedup(ratio: float) -> str:
        """Format a speedup ratio as a human-readable string"""
        if ratio >= 10:
            return f"{ratio:.0f}x"
        return f"{ratio:.1f}x"

    def create_summary(self) -> List[Dict[str, str]]:
        """Create summary table with queries and metrics per tool, plus speedup columns"""
        queries = self.get_all_queries()
        # Use fixed display order, keeping only tools present in the data
        tools = [t for t in self.TOOL_DISPLAY_ORDER if t in self.tools_data]

        self.summary = []
        for query in queries:
            row = {"Query": query}
            for tool in tools:
                metric_value = self.tools_data.get(tool, {}).get(query, "-")
                row[tool] = metric_value

            # Add speedup columns if TuringDB data is present
            turing_val = self._parse_ms(row.get("TuringDB", "-"))
            if turing_val and turing_val > 0:
                for tool in tools:
                    if tool == "TuringDB":
                        continue
                    other_val = self._parse_ms(row.get(tool, "-"))
                    col = f"Speedup vs {tool}"
                    if other_val:
                        row[col] = self._format_speedup(other_val / turing_val)
                    else:
                        row[col] = "-"

            self.summary.append(row)

        return self.summary
    
    def _get_columns(self) -> List[str]:
        """Get all data columns (tools + speedup columns) in fixed display order"""
        tools = [t for t in self.TOOL_DISPLAY_ORDER if t in self.tools_data]
        speedup_cols = [f"Speedup vs {t}" for t in tools if t != "TuringDB"]
        return tools + speedup_cols

    def save_csv(self, output_file: str = None, dataset_name: str = None) -> None:
        """Save summary as CSV"""
        if not self.summary:
            logger.warning("No data to save")
            return

        output_dir = self._ensure_output_dir(dataset_name)

        if output_file is None:
            output_file = f"report_{dataset_name}.csv" if dataset_name else "summary.csv"

        output_path = output_dir / output_file

        fieldnames = ["Query"] + self._get_columns()
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.summary)

        logger.info(f"Summary saved to {output_path}")
    
    def save_text(self, output_file: str = None, dataset_name: str = None) -> None:
        """Save summary as formatted text table"""
        if not self.summary:
            logger.warning("No data to save")
            return

        output_dir = self._ensure_output_dir(dataset_name)

        if output_file is None:
            output_file = f"report_{dataset_name}.txt" if dataset_name else "summary.txt"

        output_path = output_dir / output_file

        columns = self._get_columns()

        # Calculate column widths
        query_width = max(len("Query"), max((len(row["Query"]) for row in self.summary), default=0))
        col_widths = {col: max(len(col), max((len(row.get(col, "-")) for row in self.summary), default=0)) for col in columns}

        # Write header and rows
        header = "Query".ljust(query_width) + " | " + " | ".join(col.ljust(col_widths[col]) for col in columns)
        separator = "-" * len(header)

        with open(output_path, 'w') as f:
            f.write(separator + "\n")
            f.write(header + "\n")
            f.write(separator + "\n")

            for row in self.summary:
                query = row["Query"].ljust(query_width)
                values = " | ".join(row.get(col, "-").ljust(col_widths[col]) for col in columns)
                f.write(query + " | " + values + "\n")

            f.write(separator + "\n")

        logger.info(f"Summary saved to {output_path}")
    
    def save_markdown(self, output_file: str = None, dataset_name: str = None) -> None:
        """Save summary as markdown table"""
        if not self.summary:
            logger.warning("No data to save")
            return
        
        output_dir = self._ensure_output_dir(dataset_name)
        
        if output_file is None:
            output_file = f"report_{dataset_name}.md" if dataset_name else "summary.md"
        
        output_path = output_dir / output_file
        
        markdown_table = self._generate_markdown_table()
        with open(output_path, 'w') as f:
            f.write(markdown_table)
        
        logger.info(f"Summary saved to {output_path}")
    
    def _generate_markdown_table(self) -> str:
        """Generate markdown table as string"""
        if not self.summary:
            return ""

        columns = self._get_columns()

        # Calculate actual column widths based on content
        query_width = max(len("Query"), max((len(row["Query"]) for row in self.summary), default=5))
        col_widths = {col: max(len(col), max((len(row.get(col, "-")) for row in self.summary), default=5)) for col in columns}

        lines = []

        # Header and separator
        lines.append("| Query | " + " | ".join(columns) + " |")
        lines.append("|" + "|".join(["-" * (query_width + 2)] + ["-" * (col_widths[c] + 2) for c in columns]) + "|")

        # Data rows
        for row in self.summary:
            query = row["Query"].ljust(query_width)
            values = " | ".join(row.get(col, "-").ljust(col_widths[col]) for col in columns)
            lines.append(f"| {query} | {values} |")

        return "\n".join(lines)
    
    @staticmethod
    def _get_machine_specs() -> str:
        """Collect machine specs and return as a markdown line"""
        specs = []

        # CPU model
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        cpu_model = line.split(":", 1)[1].strip()
                        specs.append(f"**CPU**: {cpu_model}")
                        break
        except OSError:
            pass

        # CPU cores / threads
        try:
            cores = os.cpu_count()
            if cores:
                specs.append(f"**Cores**: {cores}")
        except Exception:
            pass

        # RAM
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        gb = round(kb / 1024 / 1024, 1)
                        specs.append(f"**RAM**: {gb} GB")
                        break
        except OSError:
            pass

        # OS
        try:
            result = subprocess.run(
                ["lsb_release", "-ds"],
                capture_output=True, text=True, check=True
            )
            os_name = result.stdout.strip().strip('"')
            specs.append(f"**OS**: {os_name}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            specs.append(f"**OS**: {platform.system()} {platform.release()}")

        # Storage type
        try:
            result = subprocess.run(
                ["lsblk", "-d", "-o", "NAME,ROTA", "--noheadings"],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) == 2:
                    rotational = parts[1] == "1"
                    disk_type = "HDD" if rotational else "SSD"
                    specs.append(f"**Storage**: {disk_type}")
                    break
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return " | ".join(specs)

    def _sort_benchmark_subsections(self, content: str) -> str:
        """Sort ### subsections under ## Benchmark Results alphabetically"""
        # Find the Benchmark Results section
        section_match = re.search(r"(## Benchmark Results\n+)", content)
        if not section_match:
            return content

        section_start = section_match.end()

        # Find where the section ends (next ## heading or end of file)
        next_section = re.search(r"\n## ", content[section_start:])
        section_end = section_start + next_section.start() if next_section else len(content)

        section_body = content[section_start:section_end]

        # Split into subsections (each starts with ### )
        subsections = re.split(r"(?=### )", section_body)
        subsections = [s for s in subsections if s.strip()]

        # Sort alphabetically by subsection title
        subsections.sort(key=lambda s: re.match(r"### (.+)", s).group(1).lower() if re.match(r"### (.+)", s) else "")

        sorted_body = "\n".join(s.rstrip() for s in subsections) + "\n"
        return content[:section_start] + sorted_body + content[section_end:]

    def update_readme(self, dataset_name: str) -> None:
        """Update README.md with benchmark results for specific dataset"""
        repo_root = self._get_repo_root()
        readme_path = repo_root / "README.md"

        if not readme_path.exists():
            logger.error(f"{readme_path} not found")
            return

        content = readme_path.read_text()
        markdown_table = self._generate_markdown_table()
        machine_specs = self._get_machine_specs()
        section_content = f"> {machine_specs}\n\n{markdown_table}"

        # Create dataset-specific markers
        start_marker = f"<!-- BENCHMARK_RESULTS_{dataset_name.upper()}_START -->"
        end_marker = f"<!-- BENCHMARK_RESULTS_{dataset_name.upper()}_END -->"

        # Replace existing section or add new one
        if start_marker in content:
            pattern = f"{start_marker}.*?{end_marker}"
            new_section = f"{start_marker}\n{section_content}\n{end_marker}"
            content = re.sub(pattern, new_section, content, flags=re.DOTALL)
        else:
            # Ensure Benchmark Results section exists
            if "## Benchmark Results" not in content:
                content += "\n## Benchmark Results\n\n"

            # Add new dataset subsection
            dataset_subsection = f"### {dataset_name.capitalize()}\n\n{start_marker}\n{section_content}\n{end_marker}\n\n"

            benchmark_section_match = re.search(r"(## Benchmark Results\n)", content)
            if benchmark_section_match:
                insert_pos = benchmark_section_match.end()
                content = content[:insert_pos] + dataset_subsection + content[insert_pos:]
            else:
                content += dataset_subsection

        # Sort subsections alphabetically
        content = self._sort_benchmark_subsections(content)

        readme_path.write_text(content)
        logger.info(f"README.md updated with benchmark results for {dataset_name}")
    
    def print_summary(self) -> None:
        """Print summary table to stdout"""
        if not self.summary:
            logger.warning("No data to print")
            return

        columns = self._get_columns()

        # Calculate column widths
        query_width = max(len("Query"), max((len(row["Query"]) for row in self.summary), default=0))
        col_widths = {col: max(len(col), max((len(row.get(col, "-")) for row in self.summary), default=0)) for col in columns}

        # Print header
        print("Query".ljust(query_width) + " | " + " | ".join(col.ljust(col_widths[col]) for col in columns))
        print("-" * (query_width + 3 + sum(col_widths[col] + 3 for col in columns)))

        # Print rows
        for row in self.summary:
            query = row["Query"].ljust(query_width)
            values = " | ".join(row.get(col, "-").ljust(col_widths[col]) for col in columns)
            print(query + " | " + values)


def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python parse_benchmark_report.py <report_file> [--dataset <n>] [--output-dir <path>] [--print] [--csv] [--text] [--markdown] [--update-readme]")
        logger.info("Examples:")
        logger.info("  python parse_benchmark_report.py report.txt --print")
        logger.info("  python parse_benchmark_report.py report.txt --metric min --dataset reactome --csv")
        logger.info("  python parse_benchmark_report.py report.txt --dataset pokec_small --update-readme")
        logger.info("  python parse_benchmark_report.py report.txt --dataset reactome --output-dir /custom/path --csv")
        sys.exit(1)
    
    report_file = sys.argv[1]
    dataset_name = None
    metric = "mean"
    output_dir = None
    
    # Parse --metric, --dataset, and --output-dir arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--metric" and i + 1 < len(sys.argv):
            metric = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--dataset" and i + 1 < len(sys.argv):
            dataset_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            break
    
    # Parse report
    parser = BenchmarkReportParser(report_file, metric=metric, output_dir=output_dir)
    parser.parse()
    parser.create_summary()
    
    # Handle output formats
    while i < len(sys.argv):
        if sys.argv[i] == "--print":
            parser.print_summary()
        elif sys.argv[i] == "--csv":
            parser.save_csv(dataset_name=dataset_name)
        elif sys.argv[i] == "--text":
            parser.save_text(dataset_name=dataset_name)
        elif sys.argv[i] == "--markdown":
            parser.save_markdown(dataset_name=dataset_name)
        elif sys.argv[i] == "--update-readme":
            if not dataset_name:
                logger.error("--dataset parameter is required for --update-readme")
                sys.exit(1)
            parser.update_readme(dataset_name)
        
        i += 1


if __name__ == "__main__":
    main()