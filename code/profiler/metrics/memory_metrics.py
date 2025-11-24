import tracemalloc
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MemoryCollector:
    """Collects memory usage metrics using tracemalloc."""

    def __init__(self):
        self.peak_memory = 0
        self.current_memory = 0
        self.was_tracing = False
        self.baseline_current = 0
        self.baseline_peak = 0

    def __enter__(self):
        # Check if tracemalloc was already running
        self.was_tracing = tracemalloc.is_tracing()
        
        if not self.was_tracing:
            # Start fresh
            tracemalloc.start()
            logger.debug("Started tracemalloc")
            self.baseline_current = 0
            self.baseline_peak = 0
        else:
            # Get baseline - we'll calculate delta later
            self.baseline_current, self.baseline_peak = tracemalloc.get_traced_memory()
            logger.debug(f"Baseline memory: current={self.baseline_current}, peak={self.baseline_peak}")
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            # Get current memory usage
            current, peak = tracemalloc.get_traced_memory()
            
            # Calculate deltas from baseline
            # Peak might be less than baseline if memory was freed, so use max
            self.current_memory = max(0, current - self.baseline_current)
            self.peak_memory = max(peak, self.baseline_peak) - self.baseline_peak
            
            logger.debug(f"Memory captured: current={self.current_memory}, peak={self.peak_memory} (raw: current={current}, peak={peak}, baseline_current={self.baseline_current}, baseline_peak={self.baseline_peak})")
            
            # If memory is still 0, log warning
            if self.peak_memory == 0 and self.current_memory == 0:
                logger.warning("tracemalloc reported 0 memory - this may indicate no allocations were tracked")
        except Exception as e:
            logger.error(f"Error getting traced memory: {e}")
        finally:
            # Only stop if we started it
            if not self.was_tracing and tracemalloc.is_tracing():
                tracemalloc.stop()
                logger.debug("Stopped tracemalloc")

    def get_metrics(self) -> Dict[str, int]:
        """Return collected memory metrics in bytes."""
        return {
            "current_memory": self.current_memory,
            "peak_memory": self.peak_memory
        }
