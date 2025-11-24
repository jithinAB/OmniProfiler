from typing import Dict, Any, Optional

class ProfilerComparator:
    """
    Compares two profiling reports and calculates performance differences.
    """

    def compare(self, report_a: Dict[str, Any], report_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare report_b (new) against report_a (baseline).
        Returns a dictionary containing diffs and status (improved/degraded).
        """
        comparison = {
            "time": self._compare_section(report_a, report_b, "dynamic_analysis", "time", ["wall_time", "cpu_time"]),
            "memory": self._compare_section(report_a, report_b, "dynamic_analysis", "memory", ["peak_memory", "current_memory"]),
            "gc": self._compare_gc(report_a, report_b),
            "allocations": self._compare_allocations(report_a, report_b)
        }
        return comparison

    def _compare_section(self, report_a, report_b, root_key, section_key, metrics):
        """Generic comparison for simple key-value metrics."""
        result = {}
        
        data_a = report_a.get(root_key, {}).get(section_key, {})
        data_b = report_b.get(root_key, {}).get(section_key, {})

        for metric in metrics:
            val_a = float(data_a.get(metric, 0) or 0)
            val_b = float(data_b.get(metric, 0) or 0)
            
            diff = val_b - val_a
            pct = (diff / val_a * 100) if val_a != 0 else 0.0
            
            # For these metrics, LOWER is BETTER
            if diff < 0:
                status = "improved"
            elif diff > 0:
                status = "degraded"
            else:
                status = "neutral"

            result[metric] = {
                "baseline": val_a,
                "comparison": val_b,
                "diff": diff,
                "pct": pct,
                "status": status
            }
        return result

    def _compare_gc(self, report_a, report_b):
        """Compare GC metrics."""
        result = {}
        
        gc_a = report_a.get("dynamic_analysis", {}).get("gc", {})
        gc_b = report_b.get("dynamic_analysis", {}).get("gc", {})
        
        # Total objects
        val_a = float(gc_a.get("total_objects", 0) or 0)
        val_b = float(gc_b.get("total_objects", 0) or 0)
        diff = val_b - val_a
        pct = (diff / val_a * 100) if val_a != 0 else 0.0
        
        result["total_objects"] = {
            "baseline": val_a,
            "comparison": val_b,
            "diff": diff,
            "pct": pct,
            "status": "improved" if diff < 0 else "degraded" if diff > 0 else "neutral"
        }
        
        # Collections (sum of all generations)
        col_a = sum(gc_a.get("collections", {}).values())
        col_b = sum(gc_b.get("collections", {}).values())
        diff_col = col_b - col_a
        pct_col = (diff_col / col_a * 100) if col_a != 0 else 0.0
        
        result["total_collections"] = {
            "baseline": col_a,
            "comparison": col_b,
            "diff": diff_col,
            "pct": pct_col,
            "status": "improved" if diff_col < 0 else "degraded" if diff_col > 0 else "neutral"
        }
        
        return result

    def _compare_allocations(self, report_a, report_b):
        """Compare allocation metrics."""
        result = {}
        
        alloc_a = report_a.get("dynamic_analysis", {}).get("allocations", {})
        alloc_b = report_b.get("dynamic_analysis", {}).get("allocations", {})
        
        metrics = ["total_size_bytes", "total_allocations"]
        
        for metric in metrics:
            val_a = float(alloc_a.get(metric, 0) or 0)
            val_b = float(alloc_b.get(metric, 0) or 0)
            
            diff = val_b - val_a
            pct = (diff / val_a * 100) if val_a != 0 else 0.0
            
            result[metric] = {
                "baseline": val_a,
                "comparison": val_b,
                "diff": diff,
                "pct": pct,
                "status": "improved" if diff < 0 else "degraded" if diff > 0 else "neutral"
            }
            
        return result
