import os
from typing import Dict, Any

# Try to import psutil, handle if missing
try:
    import psutil
except ImportError:
    psutil = None

class IOCollector:
    """Collects I/O metrics using psutil."""

    def __init__(self):
        self.start_io = None
        self.end_io = None
        self.process = psutil.Process(os.getpid()) if psutil else None

    def __enter__(self):
        if self.process:
            try:
                self.start_io = self.process.io_counters()
            except Exception:
                self.start_io = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            try:
                self.end_io = self.process.io_counters()
            except Exception:
                self.end_io = None

    def get_metrics(self) -> Dict[str, int]:
        """Return collected I/O metrics (bytes)."""
        metrics = {
            "read_bytes": 0,
            "write_bytes": 0,
            "read_count": 0,
            "write_count": 0
        }
        
        if self.start_io and self.end_io:
            metrics["read_bytes"] = self.end_io.read_bytes - self.start_io.read_bytes
            metrics["write_bytes"] = self.end_io.write_bytes - self.start_io.write_bytes
            metrics["read_count"] = self.end_io.read_count - self.start_io.read_count
            metrics["write_count"] = self.end_io.write_count - self.start_io.write_count
            
        return metrics
