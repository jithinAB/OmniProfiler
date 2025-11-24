"""
Memory allocation tracking using tracemalloc.
Tracks allocations by type and identifies top allocators.
"""
import tracemalloc
from typing import Dict, Any, List


class AllocationCollector:
    """Collects memory allocation statistics by type and location."""
    
    def __init__(self):
        self.snapshot = None
        self.was_tracing = False
    
    def __enter__(self):
        """Start tracking memory allocations."""
        self.was_tracing = tracemalloc.is_tracing()
        if not self.was_tracing:
            tracemalloc.start()
        return self
    
    def __exit__(self, *args):
        """Stop tracking and capture snapshot."""
        self.snapshot = tracemalloc.take_snapshot()
        # Only stop if we started it
        if not self.was_tracing and tracemalloc.is_tracing():
            tracemalloc.stop()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get memory allocation metrics.
        
        Returns:
            dict: Allocation statistics including top allocators and type breakdown
        """
        if not self.snapshot:
            return {}
        
        # Group by file/line and get top allocators
        top_stats = self.snapshot.statistics('lineno')[:10]
        
        top_allocators = []
        for stat in top_stats:
            # Extract only JSON-serializable data
            traceback_str = "Unknown"
            if stat.traceback and len(stat.traceback) > 0:
                frame = stat.traceback[0]
                traceback_str = f"{frame.filename}:{frame.lineno}"
            
            top_allocators.append({
                "file": str(traceback_str),
                "size_bytes": int(stat.size),
                "size_kb": round(float(stat.size) / 1024, 2),
                "count": int(stat.count)
            })
        
        # Calculate total allocated
        all_stats = self.snapshot.statistics('filename')
        total_size = sum(int(stat.size) for stat in all_stats)
        total_count = sum(int(stat.count) for stat in all_stats)
        
        return {
            "top_allocators": top_allocators,
            "total_size_bytes": int(total_size),
            "total_size_mb": round(float(total_size) / 1024 / 1024, 2),
            "total_allocations": int(total_count)
        }
