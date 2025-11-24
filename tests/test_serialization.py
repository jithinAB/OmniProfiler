#!/usr/bin/env python3
"""Test each collector individually for JSON serialization"""
import sys
import json
sys.path.insert(0, '/Users/jithinvg/Desktop/vlad-bud')

def test_collector(name, collector_class, *args):
    """Test if a collector's output is JSON serializable"""
    try:
        collector = collector_class(*args)
        
        # Simulate usage
        with collector:
            pass  # Empty execution
        
        metrics = collector.get_metrics()
        
        # Try to serialize
        json.dumps(metrics)
        print(f"✅ {name}: JSON serializable")
        return True
    except Exception as e:
        print(f"❌ {name}: FAILED - {e}")
        print(f"   Metrics type: {type(metrics)}")
        if isinstance(metrics, dict):
            for key, value in metrics.items():
                try:
                    json.dumps({key: value})
                except Exception as field_error:
                    print(f"   ❌ Problem in field '{key}': {type(value)} - {field_error}")
        return False

# Test each collector
from code.profiler.metrics.time_metrics import TimeCollector
from code.profiler.metrics.memory_metrics import MemoryCollector
from code.profiler.metrics.io_metrics import IOCollector
from code.profiler.metrics.gc_collector import GCCollector
from code.profiler.metrics.cpu_collector import EnhancedCPUCollector
from code.profiler.metrics.allocation_collector import AllocationCollector

print("Testing collectors for JSON serialization...\n")

test_collector("TimeCollector", TimeCollector)
test_collector("MemoryCollector", MemoryCollector)
test_collector("IOCollector", IOCollector)
test_collector("GCCollector", GCCollector)
test_collector("EnhancedCPUCollector", EnhancedCPUCollector)
test_collector("AllocationCollector", AllocationCollector)

print("\n" + "="*50)
print("Testing complete profiler output...")

from code.profiler.dynamic.profiler import DynamicProfiler

profiler = DynamicProfiler()

def dummy_func():
    x = [i for i in range(100)]
    return sum(x)

result = profiler.profile_function(dummy_func)

try:
    json_str = json.dumps(result)
    print("✅ Full profiler output: JSON serializable")
    print(f"   Size: {len(json_str)} bytes")
except Exception as e:
    print(f"❌ Full profiler output: FAILED - {e}")
    for key, value in result.items():
        try:
            json.dumps({key: value})
        except Exception as field_error:
            print(f"   ❌ Problem in field '{key}': {field_error}")
