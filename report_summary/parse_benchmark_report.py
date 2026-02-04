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
    
    def _extract_tables(self) -> Dict[str, str]:
        """Extract table content for each tool"""
        tools = {}
        
        # Look for tool headers followed by tables
        # Pattern: header with tool name, followed by table content, before next header or end
        tool_pattern = r'║ (TuringDB|Neo4j|Memgraph)\s+║.*?\n.*?\n.*?(?=╔|$)'
        
        matches = re.finditer(tool_pattern, self.content, re.DOTALL)
        
        for match in matches:
            tool_name = match.group(1)
            section = match.group(0)
            
            # Extract table content (lines with pipes and query data)
            table_lines = []
            for line in section.split('\n'):
                if '| MATCH' in line or '| CREATE' in line:
                    table_lines.append(line)
            
            if table_lines:
                tools[tool_name] = '\n'.join(table_lines)
        
        return tools
    
    def _parse_table(self, table_content: str) -> Dict[str, str]:
        """Parse table content and extract query -> mean runtime mapping"""
        query_means = {}
        
        for line in table_content.split('\n'):
            if not line.strip() or '|' not in line:
                continue
            
            # Split by pipe and extract fields
            parts = [p.strip() for p in line.split('|')]
            
            if len(parts) < 3:
                continue
            
            # Query is typically in the first meaningful column
            # Mean runtime is in the second column (index 1 after splitting)
            query = parts[1]
            mean_value = parts[2] if len(parts) > 2 else None
            
            # Validate that we have a query and mean value
            if query and mean_value and (query.startswith('MATCH') or query.startswith('CREATE')):
                query_means[query] = mean_value
        
        return query_means
    
    def parse(self) -> Dict[str, Dict[str, str]]:
        """Parse the entire report and return data for all tools"""
        tables = self._extract_tables()
        
        for tool, table_content in tables.items():
            self.tools_data[tool] = self._parse_table(table_content)
        
        return self.tools_data
    
    def get_all_queries(self) -> List[str]:
        """Get all unique queries from all tools, in order of first appearance"""
        queries = []
        seen = set()
        
        # Maintain order by iterating through content
        for line in self.content.split('\n'):
            if '| MATCH' in line or '| CREATE' in line:
                # Extract query
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 1:
                    query = parts[1]
                    if query and query not in seen:
                        queries.append(query)
                        seen.add(query)
        
        return queries
    
    def create_summary(self) -> List[Dict[str, str]]:
        """Create summary table with queries and mean runtimes per tool"""
        queries = self.get_all_queries()
        tools = list(self.tools_data.keys())
        
        summary = []
        for query in queries:
            row = {"Query": query}
            
            for tool in tools:
                mean_value = self.tools_data.get(tool, {}).get(query, "-")
                row[tool] = mean_value
            
            summary.append(row)
        
        return summary
    
    def save_csv(self, output_file: str):
        """Save summary as CSV"""
        summary = self.create_summary()
        
        if not summary:
            print("No data to save")
            return
        
        fieldnames = ["Query"] + list(self.tools_data.keys())
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary)
        
        print(f"Summary saved to {output_file}")
    
    def save_text(self, output_file: str):
        """Save summary as formatted text table"""
        summary = self.create_summary()
        
        if not summary:
            print("No data to save")
            return
        
        tools = list(self.tools_data.keys())
        
        # Calculate column widths
        query_width = max(len("Query"), max((len(row["Query"]) for row in summary), default=0))
        col_width = max(len(tool) for tool in tools)
        col_width = max(col_width, max((len(row[tool]) for row in summary for tool in tools), default=0))
        
        # Write header
        header = "Query".ljust(query_width) + " | " + " | ".join(tool.ljust(col_width) for tool in tools)
        separator = "-" * len(header)
        
        with open(output_file, 'w') as f:
            f.write(separator + "\n")
            f.write(header + "\n")
            f.write(separator + "\n")
            
            for row in summary:
                query = row["Query"].ljust(query_width)
                means = " | ".join(row[tool].ljust(col_width) for tool in tools)
                f.write(query + " | " + means + "\n")
            
            f.write(separator + "\n")
        
        print(f"Summary saved to {output_file}")
    
    def save_markdown(self, output_file: str):
        """Save summary as markdown table"""
        summary = self.create_summary()
        
        if not summary:
            print("No data to save")
            return
        
        tools = list(self.tools_data.keys())
        
        with open(output_file, 'w') as f:
            # Write header
            f.write("| Query | " + " | ".join(tools) + " |\n")
            
            # Write separator
            f.write("|" + "|".join(["-" * 80] + ["-" * 20 for _ in tools]) + "|\n")
            
            # Write rows
            for row in summary:
                query = row["Query"]
                means = " | ".join(row[tool] for tool in tools)
                f.write(f"| {query} | {means} |\n")
        
        print(f"Summary saved to {output_file}")
    
    def _generate_markdown_table(self) -> str:
        """Generate markdown table as string"""
        summary = self.create_summary()
        
        if not summary:
            return ""
        
        tools = list(self.tools_data.keys())
        lines = []
        
        # Write header
        lines.append("| Query | " + " | ".join(tools) + " |")
        
        # Write separator
        lines.append("|" + "|".join(["-" * 80] + ["-" * 20 for _ in tools]) + "|")
        
        # Write rows
        for row in summary:
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
        summary = self.create_summary()
        
        if not summary:
            print("No data to print")
            return
        
        tools = list(self.tools_data.keys())
        
        # Calculate column widths
        query_width = max(len("Query"), max((len(row["Query"]) for row in summary), default=0))
        col_width = max(len(tool) for tool in tools)
        col_width = max(col_width, max((len(row[tool]) for row in summary for tool in tools), default=0))
        
        # Print header
        print("Query".ljust(query_width) + " | " + " | ".join(tool.ljust(col_width) for tool in tools))
        print("-" * (query_width + 3 + (col_width + 3) * len(tools)))
        
        # Print rows
        for row in summary:
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
        print("  python parse_benchmark_report.py poledb_benchmark_report.txt --dataset poledb --csv --text --markdown --update-readme")
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
    parser.parse()
    
    # Print to stdout by default
    parser.print_summary()
    
    # Handle optional output formats
    while i < len(sys.argv):
        if sys.argv[i] == "--csv":
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