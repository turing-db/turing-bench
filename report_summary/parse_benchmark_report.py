#!/usr/bin/env python3
"""Parse benchmark report and create summary table"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
import csv
import subprocess


class BenchmarkReportParser:
    """Parse benchmark report files and extract mean runtimes"""
    
    def __init__(self, report_file: str):
        self.report_file = Path(report_file)
        self.content = self.report_file.read_text()
        self.tools_data: Dict[str, Dict[str, str]] = {}
        self.summary = {}
    
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
            # If git command fails, fall back to searching for .git directory
            current = Path.cwd()
            while current != current.parent:
                if (current / ".git").exists():
                    return current
                current = current.parent
            raise RuntimeError("Could not find git repository root")
    
    # def _extract_tables(self) -> Dict[str, str]:
    #     """Extract table content for each tool"""
    #     tools = {}
        
    #     # Look for tool headers and their sections
    #     # Pattern 1: Unicode box drawing characters
    #     tool_pattern1 = r'║ (TuringDB|Neo4j|Memgraph)\s+║.*?\n.*?\n.*?(?=║ |Running benchmark|Stopping|$)'
        
    #     # Pattern 2: Dashes and pipes (newer format without tool headers, detect by "Running benchmark for")
    #     # In this case we need to find tables between "Running benchmark for 'toolname'" and next benchmark
    #     lines = self.content.split('\n')
        
    #     current_tool = None
    #     table_lines = []
        
    #     for i, line in enumerate(lines):
    #         # Detect tool from "Running benchmark for 'toolname'"
    #         tool_match = re.search(r"Running benchmark for '(turingdb|memgraph|neo4j)'", line)
    #         if tool_match:
    #             # Save previous tool's table if exists
    #             if current_tool and table_lines:
    #                 tools[current_tool.capitalize()] = {
    #                     "header": header_match,
    #                     "table": '\n'.join(table_lines)
    #                 }
    #                 # tools[current_tool.capitalize()] = '\n'.join(table_lines)
    #                 table_lines = []
    #             current_tool = tool_match.group(1)

    #         # Collect table header
    #         if "Query" in line and "Mean" in line and "|" in line:
    #             # print(f"Found header: {line}")
    #             header_match = line
            
    #         # Collect table rows (lines with pipes and match/create queries)
    #         if current_tool and ('| match' in line.lower() or '| create' in line.lower()):
    #             table_lines.append(line)
        
    #     # Don't forget the last tool
    #     if current_tool and table_lines:
    #         tools[current_tool.capitalize()] = {
    #             "header": header_match,
    #             "table": '\n'.join(table_lines)
    #         } # '\n'.join(table_lines)
        
    #     # print(f"tools: {tools}")

    #     return tools

    def _extract_tables(self) -> Dict[str, Dict[str, str]]:
        """Extract table content for each tool"""
        tools = {}
        
        # Mapping to standardized tool names
        tool_name_map = {
            'turingdb': 'TuringDB',
            'neo4j': 'Neo4j',
            'memgraph': 'Memgraph'
        }
        
        lines = self.content.split('\n')
        current_tool = None
        table_lines = []
        header_match = None
        in_table = False
        
        for i, line in enumerate(lines):
            # Format 1: Detect tool from unicode box drawing header (║ TuringDB ║)
            header_box_match = re.search(r'║ (turingdb|neo4j|memgraph)\s+║', line, re.IGNORECASE)
            if header_box_match:
                # Save previous tool's table if exists
                if current_tool and table_lines and header_match:
                    tools[current_tool] = {
                        "header": header_match,
                        "table": '\n'.join(table_lines)
                    }
                    table_lines = []
                current_tool = tool_name_map[header_box_match.group(1).lower()]
                header_match = None
                in_table = False
            
            # Format 2: Detect tool from "Running benchmark for 'toolname'"
            tool_match = re.search(r"Running benchmark for ['\"]?(turingdb|neo4j|memgraph)['\"]?", line, re.IGNORECASE)
            if tool_match:
                # Save previous tool's table if exists
                if current_tool and table_lines and header_match:
                    tools[current_tool] = {
                        "header": header_match,
                        "table": '\n'.join(table_lines)
                    }
                    table_lines = []
                current_tool = tool_name_map[tool_match.group(1).lower()]
                header_match = None
                in_table = False
            
            # Detect table header (contains Query and Mean columns)
            if "Query" in line and "Mean" in line and "|" in line:
                header_match = line
                in_table = True
                continue
            
            # Collect table rows (lines with pipes and queries)
            if in_table and current_tool and ('| match' in line.lower() or '| create' in line.lower()):
                table_lines.append(line)
        
        # Don't forget the last tool
        if current_tool and table_lines and header_match:
            tools[current_tool] = {
                "header": header_match,
                "table": '\n'.join(table_lines)
            }
        
        return tools
    
    def _parse_table(self, table_info: str, metric: str = "mean") -> Dict[str, str]:
        """Parse table content and extract query -> mean runtime mapping"""
        query_metric = {}

        # print(100 * "-")

        tool_header = [elt.strip().lower() for elt in table_info["header"].split("|")]
        # print(f"header: {tool_header}")
        query_idx = tool_header.index("query")
        metric_idx = tool_header.index(metric.lower())
        # print(f"query_idx: {query_idx}\nmetric_idx: {metric_idx}")

        table_content = table_info["table"]
        
        for line in table_content.split('\n'):
            # print()
            # print(line)
            if not line.strip() or '|' not in line:
                continue
            
            # Split by pipe and extract fields
            parts = [p.strip() for p in line.split('|')]
            # print(f"parts: {parts}\n")
            
            if len(parts) < 3:
                continue
            
            # Get query and metric value
            query = parts[query_idx]
            metric_value = parts[metric_idx] # parts[2] if len(parts) > 2 else None
            # print(f"query: {query}")
            # print(f"metric_value: {metric_value}")
            
            # Validate that we have a query and mean value
            if query and metric_value and (query.startswith(('match', 'MATCH')) or query.startswith(('create', 'CREATE'))):
                query_metric[query] = metric_value

            # print(f"query_metric: {query_metric}")
            # print()
            # print(100 * "-")
        
        return query_metric
    
    def parse(self) -> Dict[str, Dict[str, str]]:
        """Parse the entire report and return data for all tools"""
        tables = self._extract_tables()
        print(100 * '-')
        print(f"tables: {tables}")
        print(100 * '-')
        print(f"tables: \n{type(tables)}\n{len(tables)}\n{tables.keys()}\n{tables['TuringDB'].keys()}")
        
        for tool, table_info in tables.items():
            self.tools_data[tool] = self._parse_table(table_info)
        
        # print(f"self.tools_data: {self.tools_data}")
        return self.tools_data
    
    def get_all_queries(self) -> List[str]:
        """Get all unique queries from all tools, in order of first appearance"""
        queries = []
        seen = set()
        
        # Maintain order by iterating through content
        for line in self.content.split('\n'):
            if '| match' in line.lower() or '| create' in line.lower():
                # Extract query - it's the first part before the Mean value
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 1:
                    query = parts[1]
                    if query and query.lower() not in seen:
                        queries.append(query)
                        seen.add(query.lower())
        
        return queries
    
    def create_summary(self) -> List[Dict[str, str]]:
        """Create summary table with queries and mean runtimes per tool"""
        queries = self.get_all_queries()
        tools = list(self.tools_data.keys())

        # print(f"queries: {queries}")
        # print(f"tools: {tools}")
        
        summary = []
        for query in queries:
            row = {"Query": query}
            
            for tool in tools:
                mean_value = self.tools_data.get(tool, {}).get(query, "-")
                row[tool] = mean_value
            
            summary.append(row)

        if not summary:
            raise ValueError("Summary table creation failed.")
        
        self.summary = summary
        # return summary
    
    
    def save_csv(self, output_file: str):
        """Save summary as CSV"""
        # summary = self.create_summary()
        
        if not self.summary:
            print("No data to save")
            return
        
        fieldnames = ["Query"] + list(self.tools_data.keys())
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.summary)
        
        print(f"Summary saved to {output_file}")
    
    def save_text(self, output_file: str):
        """Save summary as formatted text table"""
        # summary = self.create_summary()
        
        if not self.summary:
            print("No data to save")
            return
        
        tools = list(self.tools_data.keys())
        
        # Calculate column widths
        query_width = max(len("Query"), max((len(row["Query"]) for row in self.summary), default=0))
        col_width = max(len(tool) for tool in tools)
        col_width = max(col_width, max((len(row[tool]) for row in self.summary for tool in tools), default=0))
        
        # Write header
        header = "Query".ljust(query_width) + " | " + " | ".join(tool.ljust(col_width) for tool in tools)
        separator = "-" * len(header)
        
        with open(output_file, 'w') as f:
            f.write(separator + "\n")
            f.write(header + "\n")
            f.write(separator + "\n")
            
            for row in self.summary:
                query = row["Query"].ljust(query_width)
                means = " | ".join(row[tool].ljust(col_width) for tool in tools)
                f.write(query + " | " + means + "\n")
            
            f.write(separator + "\n")
        
        print(f"Summary saved to {output_file}")
    
    def save_markdown(self, output_file: str):
        """Save summary as markdown table"""
        # summary = self.create_summary()
        
        if not self.summary:
            print("No data to save")
            return
        
        tools = list(self.tools_data.keys())
        
        with open(output_file, 'w') as f:
            # Write header
            f.write("| Query | " + " | ".join(tools) + " |\n")
            
            # Write separator
            f.write("|" + "|".join(["-" * 80] + ["-" * 20 for _ in tools]) + "|\n")
            
            # Write rows
            for row in self.summary:
                query = row["Query"]
                means = " | ".join(row[tool] for tool in tools)
                f.write(f"| {query} | {means} |\n")
        
        print(f"Summary saved to {output_file}")
    
    def _generate_markdown_table(self) -> str:
        """Generate markdown table as string"""
        # summary = self.create_summary()
        
        if not self.summary:
            return ""
        
        tools = list(self.tools_data.keys())
        lines = []
        
        # Write header
        lines.append("| Query | " + " | ".join(tools) + " |")
        
        # Write separator
        lines.append("|" + "|".join(["-" * 80] + ["-" * 20 for _ in tools]) + "|")
        
        # Write rows
        for row in self.summary:
            query = row["Query"]
            means = " | ".join(row[tool] for tool in tools)
            lines.append(f"| {query} | {means} |")
        
        return "\n".join(lines)
    
    def update_readme(self, dataset_name: str):
        """Update README.md with benchmark results for specific dataset"""
        repo_root = self._get_repo_root()
        readme_path = repo_root / "README.md"
        
        if not readme_path.exists():
            print(f"Error: {readme_file} not found")
            return
        
        content = readme_path.read_text()
        markdown_table = self._generate_markdown_table()
        
        # Create dataset-specific markers
        start_marker = f"<!-- BENCHMARK_RESULTS_{dataset_name.upper()}_START -->"
        end_marker = f"<!-- BENCHMARK_RESULTS_{dataset_name.upper()}_END -->"
        
        # Check if markers already exist
        if start_marker in content:
            # Replace existing section
            pattern = f"{start_marker}.*?{end_marker}"
            new_section = f"{start_marker}\n{markdown_table}\n{end_marker}"
            content = re.sub(pattern, new_section, content, flags=re.DOTALL)
        else:
            # Add new section - ensure Benchmark Results section exists
            if "## Benchmark Results" not in content:
                # Add section at the end
                content += "\n## Benchmark Results\n\n"
            
            # Add new dataset subsection
            dataset_subsection = f"### {dataset_name.capitalize()}\n\n{start_marker}\n{markdown_table}\n{end_marker}\n\n"
            
            # Insert before the first benchmark results marker or at the end of Benchmark Results section
            benchmark_section_match = re.search(r"(## Benchmark Results\n)", content)
            if benchmark_section_match:
                insert_pos = benchmark_section_match.end()
                content = content[:insert_pos] + dataset_subsection + content[insert_pos:]
            else:
                content += dataset_subsection
        
        # Write back to file
        readme_path.write_text(content)
        print(f"README.md updated with benchmark results for {dataset_name}")
    
    def print_summary(self):
        """Print summary table to stdout"""

        # if not summary:
        #     print("No data to print")
        #     raise ValueError("Summary table is empty")
        
        tools = list(self.tools_data.keys())
        
        # Calculate column widths
        query_width = max(len("Query"), max((len(row["Query"]) for row in self.summary), default=0))
        col_width = max(len(tool) for tool in tools)
        col_width = max(col_width, max((len(row[tool]) for row in self.summary for tool in tools), default=0))
        
        # Print header
        print("Query".ljust(query_width) + " | " + " | ".join(tool.ljust(col_width) for tool in tools))
        print("-" * (query_width + 3 + (col_width + 3) * len(tools)))
        
        # Print rows
        for row in self.summary:
            query = row["Query"].ljust(query_width)
            means = " | ".join(row[tool].ljust(col_width) for tool in tools)
            print(query + " | " + means)


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_benchmark_report.py <report_file> [--dataset <name>] [--csv] [--text] [--markdown] [--update-readme]")
        print("\nExamples:")
        print("  python parse_benchmark_report.py report.txt")
        print("  python parse_benchmark_report.py report.txt --dataset reactome --csv --markdown")
        print("  python parse_benchmark_report.py report.txt --dataset pokec_small --update-readme")
        sys.exit(1)
    
    report_file = sys.argv[1]
    dataset_name = None
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--dataset" and i + 1 < len(sys.argv):
            dataset_name = sys.argv[i + 1]
            i += 2
        else:
            break
    
    parser = BenchmarkReportParser(report_file)
    # print(f"parser: {parser}")
    parser.parse()
    
    # Create summary data
    parser.create_summary()
    # print(f"summary: {self.summary}")
    
    # Print to stdout by default
    # parser.print_summary()
    
    # Handle optional output formats
    while i < len(sys.argv):
        if sys.argv[i] == "--print":
            parser.print_summary()
            i += 1
        elif sys.argv[i] == "--csv":
            if dataset_name:
                output_file = f"report_{dataset_name}.csv"
            else:
                output_file = "summary.csv"
            parser.save_csv(output_file)
            i += 1
        elif sys.argv[i] == "--text":
            if dataset_name:
                output_file = f"report_{dataset_name}.txt"
            else:
                output_file = "summary.txt"
            parser.save_text(output_file)
            i += 1
        elif sys.argv[i] == "--markdown":
            if dataset_name:
                output_file = f"report_{dataset_name}.md"
            else:
                output_file = "summary.md"
            parser.save_markdown(output_file)
            i += 1
        elif sys.argv[i] == "--update-readme":
            if not dataset_name:
                print("Error: --dataset parameter is required for --update-readme")
                sys.exit(1)
            
            # Try to find the markdown file for this dataset
            markdown_file = f"report_{dataset_name}.md"
            if not Path(markdown_file).exists():
                print(f"Warning: {markdown_file} not found, generating from parsed data")
            
            parser.update_readme(dataset_name)
            i += 1
        else:
            i += 1


if __name__ == "__main__":
    main()