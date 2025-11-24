import pytest
from code.profiler.dynamic.profiler import DynamicProfiler

def sample_function():
    total = 0
    for i in range(1000):
        total += i
    return total

def test_dynamic_profiler_execution():
    profiler = DynamicProfiler()
    metrics = profiler.profile_function(sample_function)
    
    assert metrics['time']['wall_time'] > 0
    assert metrics['memory']['peak_memory'] >= 0
    # Hotspots might be empty for such a simple function depending on cProfile resolution
    assert isinstance(metrics['hotspots'], list)
