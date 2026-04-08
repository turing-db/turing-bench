#!/usr/bin/env python3

import subprocess
import threading
from dataclasses import dataclass
from typing import Optional


def find_server_pid(engine: str) -> Optional[int]:
    """Find the PID of a running database server by engine name."""
    patterns = {
        "turingdb": "turingdb -demon",
        "neo4j": "org.neo4j.server.CommunityEntryPoint",
        "memgraph": "memgraph ",
    }
    pattern = patterns.get(engine)
    if pattern is None:
        return None
    try:
        result = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(result.stdout.strip().splitlines()[0])
    except Exception:
        pass
    return None


def read_rss_kb(pid: int) -> Optional[int]:
    """Read the RSS (Resident Set Size) in KB from /proc/<pid>/status."""
    try:
        with open(f"/proc/{pid}/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except Exception:
        pass
    return None


@dataclass
class MemoryStats:
    baseline_kb: int
    peak_kb: int
    final_kb: int


class MemorySampler:
    def __init__(self, pid: int, interval_s: float = 0.05):
        self._pid = pid
        self._interval_s = interval_s
        self._peak_kb = 0
        self._baseline_kb = 0
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _sample_loop(self) -> None:
        while not self._stop_event.is_set():
            rss = read_rss_kb(self._pid)
            if rss is not None and rss > self._peak_kb:
                self._peak_kb = rss
            self._stop_event.wait(self._interval_s)

    def start(self) -> None:
        rss = read_rss_kb(self._pid)
        self._baseline_kb = rss if rss is not None else 0
        self._peak_kb = self._baseline_kb
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> MemoryStats:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        final = read_rss_kb(self._pid)
        return MemoryStats(
            baseline_kb=self._baseline_kb,
            peak_kb=self._peak_kb,
            final_kb=final if final is not None else 0,
        )
