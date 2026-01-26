#!/usr/bin/env python3
"""
Server orchestration tool for managing database servers (TuringDB, Neo4j, Memgraph).
Handles starting and graceful shutdown.
"""

import subprocess
import sys
import os
import time
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    """Configuration for a database server"""
    name: str
    start_command: str
    start_ready_pattern: str = ""
    start_timeout: int = 30
    stop_command: Optional[str] = None
    stop_input: Optional[str] = None
    log_file: Optional[str] = None


class ServerManager:
    """Manages starting and stopping database servers"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.pid_dir = Path.home() / ".turing-bench"
        self.pid_dir.mkdir(exist_ok=True)

    def _get_pid_file(self, server_name: str) -> Path:
        """Get the PID file path for a server"""
        return self.pid_dir / f"{server_name.lower()}.pid"

    def _save_pid(self, server_name: str, pid: int) -> None:
        """Save the PID to a file"""
        self._get_pid_file(server_name).write_text(str(pid))

    def _load_pid(self, server_name: str) -> Optional[int]:
        """Load the PID from a file"""
        pid_file = self._get_pid_file(server_name)
        if pid_file.exists():
            try:
                return int(pid_file.read_text().strip())
            except (ValueError, IOError):
                return None
        return None

    def _remove_pid_file(self, server_name: str) -> None:
        """Remove the PID file"""
        pid_file = self._get_pid_file(server_name)
        if pid_file.exists():
            pid_file.unlink()

    def start(self, config: ServerConfig) -> bool:
        """Start a server and wait for it to be ready"""
        print(f"Starting {config.name}...")

        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            self.process = subprocess.Popen(
                config.start_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
            )

            self._save_pid(config.name, self.process.pid)

            if config.start_ready_pattern:
                if not self._wait_for_pattern(config.start_ready_pattern, config.start_timeout, config.log_file):
                    return False

            print(f"✓ {config.name} started")
            return True

        except Exception as e:
            print(f"✗ Failed to start {config.name}: {e}")
            return False

    def stop(self, config: ServerConfig) -> bool:
        """Stop a server gracefully"""
        saved_pid = self._load_pid(config.name)
        
        if not saved_pid:
            print(f"⚠ {config.name} is not running")
            return False

        print(f"Stopping {config.name}...")

        if config.stop_command:
            subprocess.run(config.stop_command, shell=True, capture_output=True)
            time.sleep(0.5)
        elif config.stop_input:
            if self.process and self.process.stdin:
                try:
                    self.process.stdin.write(config.stop_input)
                    self.process.stdin.flush()
                    self.process.wait()
                except Exception:
                    pass

        self._remove_pid_file(config.name)
        print(f"✓ {config.name} stopped")
        return True

    def _wait_for_pattern(self, pattern: str, timeout: int, log_file: Optional[str] = None) -> bool:
        """Wait for a pattern in process output or log file"""
        start_time = time.time()
        
        # If reading from log file
        if log_file:
            while time.time() - start_time < timeout:
                try:
                    if os.path.exists(log_file):
                        with open(log_file, 'r') as f:
                            content = f.read()
                            if pattern in content:
                                return True
                except Exception:
                    pass
                time.sleep(0.2)
            return False
        
        # Otherwise read from process stdout
        if not self.process:
            return False

        output = ""

        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                return pattern in output

            try:
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        output += line
                        if pattern in output:
                            return True
            except Exception:
                pass

        return False


# Server configurations
def _get_path(env_var: str, default: str) -> str:
    """Get path from environment variable or use default with ~ expansion"""
    if env_var in os.environ:
        return os.environ[env_var]
    return os.path.expanduser(default)


SERVERS = {
    "turingdb": ServerConfig(
        name="TuringDB",
        start_command="bash -c 'uv run turingdb > /tmp/turingdb.log 2>&1 &'",
        start_ready_pattern="Server listening",
        log_file="/tmp/turingdb.log",
        stop_command="pkill -9 turingdb",
    ),
    "neo4j": ServerConfig(
        name="Neo4j",
        start_command=f"bash -c 'source {_get_path('TURING_BENCH_HOME', '~/turing-bench')}/env.sh && neo4j start'",
        start_ready_pattern="Started neo4j",
        stop_command=f"bash -c 'source {_get_path('TURING_BENCH_HOME', '~/turing-bench')}/env.sh && neo4j stop'",
    ),
    "memgraph": ServerConfig(
        name="Memgraph",
        start_command=f"bash -c '{_get_path('TURING_BENCH_INSTALL', '~/turing-bench')}/install/memgraph/usr/lib/memgraph/memgraph --log-file=./memgraph/logs/memgraph.log --data-directory=./memgraph/data/ --bolt-port=7688'",
        start_ready_pattern="You are running Memgraph v",
        stop_command="pkill -9 memgraph",
    ),
}


def print_header(text: str) -> None:
    """Print a formatted header"""
    print()
    print("╔════════════════════════════════╗")
    print(f"║ {text:<30} ║")
    print("╚════════════════════════════════╝")
    print()


def main():
    """Main orchestration function"""
    parser = argparse.ArgumentParser(
        description="Manage database servers (TuringDB, Neo4j, Memgraph)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s turingdb start          # Start TuringDB
  %(prog)s neo4j stop              # Stop Neo4j
  %(prog)s all start               # Start all servers
        """
    )
    
    parser.add_argument(
        "server",
        choices=["turingdb", "neo4j", "memgraph", "all"],
        help="Server to manage (or 'all' for all servers)"
    )
    
    parser.add_argument(
        "action",
        choices=["start", "stop"],
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    server_map = {
        "turingdb": [SERVERS["turingdb"]],
        "neo4j": [SERVERS["neo4j"]],
        "memgraph": [SERVERS["memgraph"]],
        "all": SERVERS,
    }
    
    servers_to_manage = server_map[args.server]
    manager = ServerManager()
    failed = False
    
    for config in servers_to_manage:
        print_header(config.name)
        
        if args.action == "start":
            if not manager.start(config):
                failed = True
        else:
            if not manager.stop(config):
                failed = True
    
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()