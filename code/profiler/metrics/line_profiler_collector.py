"""
Line-level profiling collector using line_profiler library.
"""
import inspect
from typing import Dict, Any, Callable
from line_profiler import LineProfiler


class LineProfilerCollector:
    """Collects line-by-line profiling data for functions."""
    
    def __init__(self):
        self.profiler = LineProfiler()
    
    def add_function(self, func: Callable):
        """Add a function to be profiled."""
        try:
            self.profiler.add_function(func)
        except Exception:
            pass  # Skip if function can't be profiled
    
    def enable(self):
        """Enable profiling."""
        self.profiler.enable()
    
    def disable(self):
        """Disable profiling."""
        self.profiler.disable()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Extract line-level statistics.
        Returns dict mapping function names to their line stats.
        """
        stats = {}
        
        try:
            for func, timings in self.profiler.get_stats().timings.items():
                filename, start_lineno, func_name = func
                
                # Skip built-in and library functions
                if '<' in filename or 'lib/python' in filename:
                    continue
                
                # Get source code
                try:
                    source_lines = inspect.getsourcelines(timings[0][0])[0]
                    source_code = ''.join(source_lines)
                except Exception:
                    source_code = None
                
                # Process line timings
                line_stats = {}
                for lineno, nhits, time in timings:
                    if nhits > 0:
                        line_stats[str(lineno)] = {
                            "hits": nhits,
                            "time_us": time,
                            "time_ms": round(time / 1000, 3),
                            "time_per_hit_us": round(time / nhits, 2) if nhits > 0 else 0
                        }
                
                stats[func_name] = {
                    "filename": filename,
                    "start_line": start_lineno,
                    "source": source_code,
                    "lines": line_stats
                }
        
        except Exception as e:
            # If line_profiler fails, return empty
            pass
        
        return stats
