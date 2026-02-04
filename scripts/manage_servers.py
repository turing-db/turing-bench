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

CLEARLINE = "\r\033[K"


@dataclass
class ServerConfig:
    """Configuration for a database server"""

    name: str
    start_command: str
    start_ready_pattern: str = ""
    start_timeout: int = 30
    stop_timeout: int = 30
    stop_command: Optional[str] = None
    stop_input: Optional[str] = None
    log_file: Optional[str] = None


class ServerManager:
    """Manages starting and stopping database servers"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.pid_dir = Path(__file__).parent / ".cache"
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

    def _is_process_alive(self, pid: int) -> bool:
        """Check if a process with the given PID is actually running"""
        result = subprocess.run(f"ps -p {pid}", shell=True, stdout=subprocess.PIPE)
        return result.returncode == 0

    def _is_neo4j_running(self) -> bool:
        """Check if Neo4j is actually running"""
        result = subprocess.run(
            "ps aux | grep 'org.neo4j.server.CommunityEntryPoint' | grep -v grep",
            shell=True,
            capture_output=True,
        )
        return result.returncode == 0

    def _is_memgraph_running(self) -> bool:
        """Check if Neo4j is actually running"""
        result = subprocess.run(
            "echo 'RETURN 1;' | mgconsole --port 7688",
            shell=True,
            capture_output=True,
        )
        return result.returncode == 0

    def start(self, config: ServerConfig, additional_args: str) -> bool:
        """Start a server and wait for it to be ready"""

        # Special handling for Neo4j - check by process name instead of PID
        if config.name == "Neo4j":
            if self._is_neo4j_running():
                print(f"{CLEARLINE}⚠ {config.name} is already running", end="")
                return False
        else:
            # Original logic for TuringDB and Memgraph
            saved_pid = self._load_pid(config.name)

            if saved_pid and self._is_process_alive(saved_pid):
                print(f"{CLEARLINE}⚠ {config.name} is already running", end="")
                return False
            elif saved_pid:
                self._remove_pid_file(config.name)

        print(f"{CLEARLINE}○ Starting {config.name}...", end="")

        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"

            self.process = subprocess.Popen(
                f"{config.start_command} {additional_args}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
            )

            self._save_pid(config.name, self.process.pid)

            if config.name == "Memgraph":
                if not self._wait_for_memgraph_ready(config):
                    return False
            elif config.name == "TuringDB":
                if not self._wait_for_turingdb_ready(config):
                    return False
            elif config.name == "Neo4j":
                if not self._wait_for_pattern(
                    config.start_ready_pattern, config.start_timeout, config.log_file
                ):
                    return False
            else:
                raise Exception(f"Unknown server type: {config.name}")

            print(f"{CLEARLINE}✓ {config.name} started", end="")
            return True

        except Exception as e:
            print(f"{CLEARLINE}✗ Failed to start {config.name}: {e}", end="")
            return False

    def stop(self, config: ServerConfig, additional_args: str) -> bool:
        """Stop a server gracefully"""
        saved_pid = self._load_pid(config.name)

        if not saved_pid:
            print(f"{CLEARLINE}⚠ {config.name} is not running", end="")
            return False

        print(f"{CLEARLINE}  Stopping {config.name}...", end="")

        if config.stop_command:
            subprocess.run(f"{config.stop_command} {additional_args}", shell=True, capture_output=True)
        elif config.stop_input:
            if self.process and self.process.stdin:
                try:
                    self.process.stdin.write(config.stop_input)
                    self.process.stdin.flush()
                    self.process.wait()
                except Exception:
                    pass

        # Verify server actually stopped (handles both blocking and non-blocking stop commands)
        if not self._verify_server_stopped(config):
            print(f"{CLEARLINE}✗ Failed to stop {config.name} within timeout", end="")
            return False

        self._remove_pid_file(config.name)
        print(f"{CLEARLINE}✓ {config.name} stopped", end="")
        return True

    def _verify_server_stopped(
        self, config: ServerConfig, check_interval: float = 1.0
    ) -> bool:
        """Verify that a server has actually stopped within timeout"""
        start_time = time.time()

        while time.time() - start_time < config.stop_timeout:
            # Check if server is still running based on server type
            if config.name == "Neo4j":
                is_running = self._is_neo4j_running()
            elif config.name == "Memgraph":
                is_running = self._is_memgraph_running()
            else:
                # For TuringDB and Memgraph
                saved_pid = self._load_pid(config.name)
                is_running = saved_pid is not None and self._is_process_alive(saved_pid)

            # If server is stopped, we're done
            if not is_running:
                return True

            # Still running, wait a bit and check again
            time.sleep(check_interval)

        # Timeout reached and server is still running
        return False

    def _wait_for_memgraph_ready(self, config: ServerConfig) -> bool:
        """Wait for Memgraph to be ready"""
        start_time = time.time()

        while time.time() - start_time < config.stop_timeout:
            if self.process and self.process.poll() is not None:
                return False

            try:
                res = subprocess.run(
                    f"echo 'RETURN 1;' | mgconsole --port 7688",
                    shell=True,
                    capture_output=True,
                )
                if res.returncode == 0:
                    return True

                time.sleep(1.0)
            except Exception:
                pass

        return False

    def _wait_for_turingdb_ready(self, config: ServerConfig) -> bool:
        """Wait for TuringDB to be ready"""
        start_time = time.time()

        while time.time() - start_time < config.stop_timeout:
            try:
                cmd = "uv run python3 -c 'import turingdb; c = turingdb.TuringDB(); c.warmup()'"
                res = subprocess.run(cmd, shell=True, capture_output=True)
                if res.returncode == 0:
                    return True

                time.sleep(1.0)
            except Exception:
                pass

        return False

    def _wait_for_pattern(
        self, pattern: str, timeout: int, log_file: Optional[str] = None
    ) -> bool:
        """Wait for a pattern in process output or log file"""
        start_time = time.time()

        # If reading from log file
        if log_file:
            while time.time() - start_time < timeout:
                try:
                    if os.path.exists(log_file):
                        with open(log_file, "r") as f:
                            content = f.read()
                            if pattern in content:
                                return True
                except Exception:
                    pass
                time.sleep(1.0)
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
def _get_repo_root() -> Path:
    """Get the absolute path to the repository root"""
    # Script is at servers_python/manage_servers.py
    return Path(__file__).parent.parent


repo_root = _get_repo_root()
install_folder = (repo_root / "install").absolute()

MEMGRAPH_BINARY = f"{install_folder}/memgraph/usr/lib/memgraph/memgraph"
MEMGRAPH_LOG_FILE = f"{install_folder}/memgraph/log"

SERVERS = {
    "turingdb": ServerConfig(
        name="TuringDB",
        start_command=f"turingdb -demon",
        stop_command="pkill -15 turingdb",
    ),
    "neo4j": ServerConfig(
        name="Neo4j",
        start_command=f"neo4j start",
        start_ready_pattern="Started neo4j",
        stop_command=f"neo4j stop",
    ),
    "memgraph": ServerConfig(
        name="Memgraph",
        start_command=f"{MEMGRAPH_BINARY} "
        + f"--log-file={MEMGRAPH_LOG_FILE} "
        + f"--storage-mode=IN_MEMORY_ANALYTICAL "
        + f"--bolt-port=7688",
        stop_command="pkill -15 memgraph",
        start_timeout=120,
        stop_timeout=120,
    ),
}


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
        """,
    )

    parser.add_argument(
        "server",
        choices=["turingdb", "neo4j", "memgraph", "all"],
        help="Server to manage (or 'all' for all servers)",
    )

    parser.add_argument("action", choices=["start", "stop"], help="Action to perform")
    parser.add_argument('additional', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    server_map = {
        "turingdb": [SERVERS["turingdb"]],
        "neo4j": [SERVERS["neo4j"]],
        "memgraph": [SERVERS["memgraph"]],
        "all": list(SERVERS.values()),
    }

    servers_to_manage = server_map[args.server]
    manager = ServerManager()
    failed = False

    for config in servers_to_manage:
        if args.action == "start":
            if not manager.start(config, " ".join(args.additional)):
                failed = True
        else:
            if not manager.stop(config, " ".join(args.additional)):
                failed = True
    print()

    if failed:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
