from code.profiler.comparator import ProfilerComparator
import json

# Mock reports
report_a = {
    "dynamic_analysis": {
        "time": {"wall_time": 1.0, "cpu_time": 0.8},
        "memory": {"peak_memory": 1000},
        "gc": {
            "total_objects": 100,
            "collections": {"gen0": 10, "gen1": 0, "gen2": 0}
        },
        "allocations": {"total_size_bytes": 5000, "total_allocations": 50}
    }
}

report_b = {
    "dynamic_analysis": {
        "time": {"wall_time": 0.5, "cpu_time": 0.4}, # Improved (50% less)
        "memory": {"peak_memory": 1200}, # Degraded (20% more)
        "gc": {
            "total_objects": 80, # Improved
            "collections": {"gen0": 5, "gen1": 0, "gen2": 0} # Improved
        },
        "allocations": {"total_size_bytes": 5000, "total_allocations": 50} # Neutral
    }
}

comparator = ProfilerComparator()
result = comparator.compare(report_a, report_b)

print(json.dumps(result, indent=2))

# Assertions
assert result["time"]["wall_time"]["status"] == "improved"
assert result["memory"]["peak_memory"]["status"] == "degraded"
assert result["allocations"]["total_size_bytes"]["status"] == "neutral"
print("\n✅ Comparison logic verified!")
