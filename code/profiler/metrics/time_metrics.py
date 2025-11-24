import time
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, List

class TimeCollector:
    """Collects execution time metrics with latency distribution."""
    
    def __init__(self, track_samples=False):
        self.start_time = 0.0
        self.end_time = 0.0
        self.start_cpu = 0.0
        self.end_cpu = 0.0
        self.track_samples = track_samples
        self.samples = []  # For percentile calculations

    def __enter__(self):
        self.start_time = time.perf_counter()
        self.start_cpu = time.process_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.end_cpu = time.process_time()
        
        if self.track_samples:
            self.samples.append(self.end_time - self.start_time)

    def get_metrics(self) -> Dict[str, Any]:
        """Return collected time metrics with optional percentiles."""
        wall_time = self.end_time - self.start_time
        cpu_time = self.end_cpu - self.start_cpu
        
        metrics = {
            "wall_time": wall_time,
            "cpu_time": cpu_time
        }
        
        # Add percentiles if we have samples
        if self.samples and len(self.samples) > 0:
            metrics["percentiles"] = {
                "p50": float(np.percentile(self.samples, 50)),
                "p95": float(np.percentile(self.samples, 95)),
                "p99": float(np.percentile(self.samples, 99)),
                "min": float(min(self.samples)),
                "max": float(max(self.samples)),
                "mean": float(np.mean(self.samples)),
                "std": float(np.std(self.samples))
            }
        
        return metrics

