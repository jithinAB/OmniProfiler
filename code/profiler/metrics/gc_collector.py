"""
Garbage Collector metrics collector.
Tracks GC collections, object counts, and GC overhead.
"""
import gc
import time
from typing import Dict, Any


class GCCollector:
    """Collects Python garbage collector statistics."""
    
    def __init__(self):
        self.start_stats = None
        self.start_count = None
        self.start_time = None
        self.gc_time = 0
    
    def __enter__(self):
        """Start collecting GC metrics."""
        # Force a collection to start fresh
        gc.collect()
        
        self.start_stats = gc.get_stats()
        self.start_count = gc.get_count()
        self.start_time = time.time()
        
        return self
    
    def __exit__(self, *args):
        """Stop collecting and capture final state."""
        self.end_stats = gc.get_stats()
        self.end_count = gc.get_count()
        self.gc_time = time.time() - self.start_time
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get GC metrics including collections per generation and object counts.
        
        Returns:
            dict: GC statistics with collections, objects, and thresholds
        """
        if not self.start_count or not self.end_count:
            return {}
        
        # Calculate collections that occurred during profiling
        collections = {
            "gen0": self.end_count[0] - self.start_count[0],
            "gen1": self.end_count[1] - self.start_count[1],
            "gen2": self.end_count[2] - self.start_count[2]
        }
        
        # Current object counts per generation
        current_objects = {
            "gen0": gc.get_count()[0],
            "gen1": gc.get_count()[1],
            "gen2": gc.get_count()[2]
        }
        
        # GC thresholds
        thresholds = gc.get_threshold()
        
        # Total tracked objects
        total_objects = len(gc.get_objects())
        
        return {
            "collections": collections,
            "objects_per_gen": current_objects,
            "total_objects": total_objects,
            "thresholds": {
                "gen0": thresholds[0],
                "gen1": thresholds[1],
                "gen2": thresholds[2]
            },
            "is_enabled": gc.isenabled()
        }
