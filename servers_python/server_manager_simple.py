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
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Callable


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
        if not self.process or self.process.poll() is not None:
            print(f"⚠ {config.name} is not running")
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
                if result.returncode != 0:
                    print(f"  Warning: stop command returned {result.returncode}")
                    if result.stderr:
                        print(f"  Error: {result.stderr}")
            # Use stop_input if provided (e.g., "exit\n" for interactive shells)
            elif config.stop_input:
                print(f"  Sending: {repr(config.stop_input)}")
                try:
                    self.process.stdin.write(config.stop_input)
                    self.process.stdin.flush()
                except Exception as e:
                    print(f"  Warning: Could not send input: {e}")
            else:
                # Send signal for graceful shutdown
                signal_map = {
                    "SIGTERM": signal.SIGTERM,
                    "SIGINT": signal.SIGINT,
                }
                sig = signal_map.get(config.stop_signal, signal.SIGTERM)
                self.process.send_signal(sig)

            print(f"  Waiting for process to exit...")
            
            # Wait for process to exit
            self.process.wait()
            print(f"✓ {config.name} stopped")
            return True

        except Exception as e:
            print(f"✗ Failed to stop {config.name}: {e}")
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
                    except:
                        pass
                
                if pattern in self.output_buffer:
                    return True
                
                print(f"  ✗ Process exited before message found")
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
        start_command="uv run turingdb",
        stop_signal="SIGINT",
        start_ready_pattern="Server listening",
        stop_pattern="",
        stop_input="exit\n",  # Send "exit" to the interactive prompt
    ),
    ServerConfig(
        name="Neo4j",
        start_command="bash -c 'source env.sh && neo4j start'",
        stop_signal="SIGINT",
        start_ready_pattern="Started neo4j",
        stop_command="bash -c 'source env.sh && neo4j stop'",  # Run separate stop command
    ),
    ServerConfig(
        name="Memgraph",
        start_command=f"bash -c '{_get_path('TURING_BENCH_INSTALL', '~/turing-bench')}/install/memgraph/usr/lib/memgraph/memgraph --log-file=./memgraph/logs/memgraph.log --data-directory=./memgraph/data/ --bolt-port=7688'",
        stop_signal="SIGINT",
        start_ready_pattern="You are running Memgraph v",
        stop_command="pkill -f memgraph",  # Force kill memgraph process
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
    """Main orchestration function"""
    manager = ServerManager()
    failed = False

    for config in SERVERS:
        print_tool_header(config.name)

        # Start
        print_section_header("Starting")
        if not manager.start(config):
            failed = True
            continue

        # Stop
        print_section_header("Stopping")
        if not manager.stop(config):
            failed = True

    # Final message
    print_tool_header("Complete")
    if failed:
        print("⚠ Some servers failed!")
        sys.exit(1)
    else:
        print("✓ All servers started and stopped successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()