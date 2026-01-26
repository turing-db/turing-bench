#!/usr/bin/env python3
"""
Server orchestration tool for managing database servers (TuringDB, Neo4j, Memgraph).
Handles starting, monitoring readiness, and graceful shutdown.
"""

import subprocess
import time
import signal
import sys
import os
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    """Configuration for a database server"""
    name: str
    start_command: str  # Shell command to start the server
    stop_signal: str = "SIGTERM"  # Signal to send for graceful shutdown
    start_ready_pattern: str = ""  # Regex pattern to detect server is ready
    stop_pattern: str = ""  # Pattern to detect server has stopped
    start_timeout: int = 30
    stop_timeout: int = 30
    cwd: Optional[str] = None
    stop_input: Optional[str] = None  # Text to send to stdin for graceful shutdown (e.g., "exit\n")
    stop_command: Optional[str] = None  # Separate command to stop the server (e.g., "neo4j stop")


class ServerManager:
    """Manages starting and stopping database servers"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.output_buffer = ""
        self.pid_dir = Path.home() / ".turing-bench"
        self.pid_dir.mkdir(exist_ok=True)

    def _get_pid_file(self, server_name: str) -> Path:
        """Get the PID file path for a server"""
        return self.pid_dir / f"{server_name.lower()}.pid"

    def _save_pid(self, server_name: str, pid: int) -> None:
        """Save the PID to a file"""
        pid_file = self._get_pid_file(server_name)
        pid_file.write_text(str(pid))
        print(f"  PID saved to {pid_file}")

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
                stdin=subprocess.PIPE,  # Enable stdin for interactive input
                cwd=config.cwd,
                text=True,
                bufsize=1,
                env=env,
            )

            # Save the PID for later use
            self._save_pid(config.name, self.process.pid)

            # Wait for ready signal if specified
            if config.start_ready_pattern:
                if not self._wait_for_pattern(
                    config.start_ready_pattern,
                    config.start_timeout,
                    "startup"
                ):
                    self.terminate()
                    return False

            print(f"✓ {config.name} is ready!")
            return True

        except Exception as e:
            print(f"✗ Failed to start {config.name}: {e}")
            return False

    def stop(self, config: ServerConfig) -> bool:
        """Stop a server gracefully"""
        # Try to load the PID from file if process is not loaded
        if not self.process or self.process.poll() is not None:
            saved_pid = self._load_pid(config.name)
            if saved_pid:
                print(f"  Found saved PID: {saved_pid}")
                # For a saved PID, we can't interact with it directly via stdin
                # We'll use the stop_command or stop_signal instead
                self.process = None
            
            if not self.process and not saved_pid:
                print(f"⚠ {config.name} is not running")
                self._remove_pid_file(config.name)
                return False

        print(f"Stopping {config.name}...")

        try:
            # Use stop_command if provided (e.g., "neo4j stop")
            if config.stop_command:
                print(f"  Running: {config.stop_command}")
                result = subprocess.run(
                    config.stop_command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0 and result.returncode != -15:
                    print(f"  Warning: stop command returned {result.returncode}")
                    if result.stderr:
                        print(f"  Error: {result.stderr}")
            # Use stop_input if provided (e.g., "exit\n" for interactive shells)
            # Only works if we have an active process with stdin
            elif config.stop_input and self.process and self.process.stdin:
                print(f"  Sending: {repr(config.stop_input)}")
                try:
                    self.process.stdin.write(config.stop_input)
                    self.process.stdin.flush()
                except Exception as e:
                    print(f"  Warning: Could not send input: {e}")
            else:
                # Send signal for graceful shutdown
                if self.process:
                    signal_map = {
                        "SIGTERM": signal.SIGTERM,
                        "SIGINT": signal.SIGINT,
                    }
                    sig = signal_map.get(config.stop_signal, signal.SIGTERM)
                    self.process.send_signal(sig)

            print("  Waiting for process to exit...")
            
            # Wait for process to exit if we have one
            if self.process:
                self.process.wait()
            else:
                # If we don't have a process object, wait a bit for the stop command to take effect
                time.sleep(1)
            
            # Remove the PID file
            self._remove_pid_file(config.name)
            
            print(f"✓ {config.name} stopped")
            return True

        except Exception as e:
            print(f"✗ Failed to stop {config.name}: {e}")
            self._remove_pid_file(config.name)
            return False

    def terminate(self):
        """Forcefully terminate the process"""
        if self.process:
            self.process.kill()
            self.process.wait()

    def _wait_for_pattern(
        self,
        pattern: str,
        timeout: int,
        phase: str
    ) -> bool:
        """Wait for a pattern to appear in process output"""
        if not self.process:
            return False
        
        print(f"  Waiting for {phase} (looking for: '{pattern}')...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if process died
            if self.process.poll() is not None:
                # Read remaining output
                if self.process.stdout:
                    try:
                        remaining = self.process.stdout.read()
                        if remaining:
                            self.output_buffer += remaining
                            print(f"    {remaining.rstrip()}")
                    except Exception:
                        pass
                
                if pattern in self.output_buffer:
                    return True
                
                print("  ✗ Process exited before message found")
                return False

            # Read available output
            try:
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        self.output_buffer += line
                        # Print for visibility
                        print(f"    {line.rstrip()}")
                        
                        if pattern in self.output_buffer:
                            return True
                    else:
                        time.sleep(0.05)
            except Exception:
                time.sleep(0.05)

        print(f"  ✗ Timeout waiting for {phase}")
        return False


# Helper function to get configurable paths
def _get_path(env_var: str, default: str) -> str:
    """Get path from environment variable or use default with ~ expansion"""
    if env_var in os.environ:
        return os.environ[env_var]
    return os.path.expanduser(default)


# Server configurations
SERVERS = [
    ServerConfig(
        name="TuringDB",
        start_command=f"cd {_get_path('TURINGDB_HOME', '~/turingdb-python')} && uv run turingdb",
        stop_signal="SIGINT",
        start_ready_pattern="Server listening",
        stop_pattern="",
        stop_timeout=5,
        stop_input="exit\n",  # Send "exit" to the interactive prompt
    ),
    ServerConfig(
        name="Neo4j",
        start_command=f"bash -c 'source {_get_path('TURING_BENCH_HOME', '~/turing-bench')}/env.sh && neo4j start'",
        stop_signal="SIGINT",
        start_ready_pattern="Started neo4j",
        stop_command=f"bash -c 'source {_get_path('TURING_BENCH_HOME', '~/turing-bench')}/env.sh && neo4j stop'",
        stop_pattern="",
    ),
    ServerConfig(
        name="Memgraph",
        start_command=f"bash -c '{_get_path('TURING_BENCH_INSTALL', '~/turing-bench')}/install/memgraph/usr/lib/memgraph/memgraph --log-file=./memgraph/logs/memgraph.log --data-directory=./memgraph/data/ --bolt-port=7688'",
        stop_signal="SIGINT",
        start_ready_pattern="You are running Memgraph v",
        stop_command="pkill -f memgraph",
        stop_pattern="",
    ),
]


def print_tool_header(text: str) -> None:
    """Print a formatted tool header"""
    print()
    print("╔════════════════════════════════╗")
    print(f"║ {text:<30} ║")
    print("╚════════════════════════════════╝")
    print()


def print_section_header(text: str) -> None:
    """Print a formatted section header"""
    print()
    print(f"--- {text} ---")
    print()


def main():
    """Main orchestration function with CLI argument support"""
    parser = argparse.ArgumentParser(
        description="Manage database servers (TuringDB, Neo4j, Memgraph)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s turingdb start          # Start TuringDB
  %(prog)s neo4j stop              # Stop Neo4j
  %(prog)s memgraph start          # Start Memgraph
  %(prog)s all start               # Start all servers
  %(prog)s all stop                # Stop all servers
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
    
    # Get the servers to manage
    server_map = {
        "turingdb": [SERVERS[0]],
        "neo4j": [SERVERS[1]],
        "memgraph": [SERVERS[2]],
        "all": SERVERS,
    }
    
    servers_to_manage = server_map[args.server]
    
    # Perform the action
    manager = ServerManager()
    failed = False
    
    for config in servers_to_manage:
        if args.action == "start":
            print_tool_header(config.name)
            print_section_header("Starting")
            if not manager.start(config):
                failed = True
        else:  # stop
            print_tool_header(config.name)
            print_section_header("Stopping")
            if not manager.stop(config):
                failed = True
    
    # Final message
    if not servers_to_manage:
        print("No servers selected")
        sys.exit(1)
    
    if len(servers_to_manage) == 1:
        server_name = servers_to_manage[0].name
        if failed:
            print(f"⚠ Failed to {args.action} {server_name}!")
            sys.exit(1)
        else:
            print(f"✓ {server_name} {args.action}ed successfully!")
            sys.exit(0)
    else:
        if failed:
            print(f"⚠ Some servers failed to {args.action}!")
            sys.exit(1)
        else:
            print(f"✓ All servers {args.action}ed successfully!")
            sys.exit(0)


if __name__ == "__main__":
    main()