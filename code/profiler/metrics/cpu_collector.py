"""
Enhanced CPU metrics collector using psutil.
Tracks user/system CPU time, utilization, and context switches.
"""
import os
import psutil
from typing import Dict, Any
import logging

# Try to import resource module (Unix/macOS only)
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False
    resource = None

logger = logging.getLogger(__name__)


class EnhancedCPUCollector:
    """Collects detailed CPU usage metrics."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_cpu = None
        self.start_ctx_switches = None
        self.start_rusage = None
        self.end_cpu = None
        self.end_ctx_switches = None
    
    def __enter__(self):
        """Start collecting CPU metrics."""
        self.start_cpu = self.process.cpu_times()
        
        # Try to get context switches from psutil (cross-platform)
        try:
            self.start_ctx_switches = self.process.num_ctx_switches()
        except AttributeError:
            # Not supported on all platforms
            self.start_ctx_switches = None
            
        # Try to get resource usage (Unix/macOS only, more reliable)
        if HAS_RESOURCE:
            try:
                self.start_rusage = resource.getrusage(resource.RUSAGE_SELF)
            except Exception as e:
                logger.debug(f"Failed to get resource usage: {e}")
                self.start_rusage = None
        
        return self
    
    def __exit__(self, *args):
        """Stop collecting and capture final state."""
        self.end_cpu = self.process.cpu_times()
        try:
            self.end_ctx_switches = self.process.num_ctx_switches()
        except AttributeError:
            self.end_ctx_switches = None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get enhanced CPU metrics.
        
        Returns:
            dict: CPU statistics including user/system time and context switches
        """
        if not self.start_cpu or not self.end_cpu:
            return {}
        
        metrics = {
            "user_time": self.end_cpu.user - self.start_cpu.user,
            "system_time": self.end_cpu.system - self.start_cpu.system,
            "cpu_percent": self.process.cpu_percent(interval=None)
        }
        
        # Add context switches if available
        # Prefer resource module (Unix/macOS) for more reliable data
        if HAS_RESOURCE and self.start_rusage:
            try:
                usage = resource.getrusage(resource.RUSAGE_SELF)
                vol_delta = usage.ru_nvcsw - self.start_rusage.ru_nvcsw
                invol_delta = usage.ru_nivcsw - self.start_rusage.ru_nivcsw
                
                metrics["context_switches"] = {
                    "voluntary": max(0, vol_delta),
                    "involuntary": max(0, invol_delta)
                }
                return metrics
            except Exception as e:
                logger.debug(f"Failed to get context switches from resource module: {e}")
        
        # Fallback to psutil (Windows and other platforms)
        if self.start_ctx_switches and self.end_ctx_switches:
            try:
                vol_delta = self.end_ctx_switches.voluntary - self.start_ctx_switches.voluntary
                invol_delta = self.end_ctx_switches.involuntary - self.start_ctx_switches.involuntary
                
                metrics["context_switches"] = {
                    "voluntary": max(0, vol_delta),
                    "involuntary": max(0, invol_delta)
                }
            except Exception as e:
                logger.debug(f"Failed to get context switches from psutil: {e}")
        
        return metrics
