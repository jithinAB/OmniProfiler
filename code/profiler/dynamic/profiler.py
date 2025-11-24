import cProfile
import pstats
import io
try:
    from pyinstrument import Profiler
except ImportError:
    Profiler = None

from typing import Callable, Dict, Any, List
from code.profiler.metrics.time_metrics import TimeCollector
from code.profiler.metrics.memory_metrics import MemoryCollector
from code.profiler.metrics.io_metrics import IOCollector
from code.profiler.metrics.gc_collector import GCCollector
from code.profiler.metrics.cpu_collector import EnhancedCPUCollector
from code.profiler.metrics.allocation_collector import AllocationCollector

import logging

# Configure logging
logging.basicConfig(
    filename='profiler_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(process)d - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DynamicProfiler:
    """
    Orchestrates dynamic profiling using multiple collectors.
    """

    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Profile a single function execution.
        """
        logger.debug("Starting profile_function")
        time_collector = TimeCollector()
        mem_collector = MemoryCollector()
        io_collector = IOCollector()
        gc_collector = GCCollector()
        cpu_collector = EnhancedCPUCollector()
        allocation_collector = AllocationCollector()
        
        # cProfile for hotspots
        pr = cProfile.Profile()
        
        # pyinstrument for call tree
        tree_profiler = None
        if Profiler:
            tree_profiler = Profiler()
        else:
            logger.debug("pyinstrument not available, call tree will not be generated")

        error = None
        result = None
        try:
            with time_collector, mem_collector, io_collector, gc_collector, cpu_collector, allocation_collector:
                pr.enable()
                if tree_profiler:
                    tree_profiler.start()
                
                result = func(*args, **kwargs)
                
        except Exception as e:
            logger.error(f"Exception in profile_function: {e}")
            error = str(e)
        finally:
            if tree_profiler:
                if tree_profiler.is_running:
                    tree_profiler.stop()
            pr.disable()

        # Process hotspots
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        hotspots = self._parse_hotspots(s.getvalue())

        # Process call tree
        call_tree_data = {}
        if tree_profiler:
            # Use JSON renderer for structured data
            from pyinstrument.renderers import JSONRenderer
            renderer = JSONRenderer()
            json_output = renderer.render(tree_profiler.last_session)
            
            # Parse it back to a dict so it's nested in the final report
            import json
            try:
                call_tree_data = json.loads(json_output)
            except:
                call_tree_data = {}

        time_metrics = time_collector.get_metrics()
        mem_metrics = mem_collector.get_metrics()
        io_metrics = io_collector.get_metrics()
        time_metrics = time_collector.get_metrics()
        mem_metrics = mem_collector.get_metrics()
        io_metrics = io_collector.get_metrics()
        gc_metrics = gc_collector.get_metrics()
        cpu_metrics = cpu_collector.get_metrics()
        allocation_metrics = allocation_collector.get_metrics()

        logger.debug(f"Time Metrics: {time_metrics}")
        logger.debug(f"Memory Metrics: {mem_metrics}")
        logger.debug(f"IO Metrics: {io_metrics}")
        logger.debug(f"GC Metrics: {gc_metrics}")
        logger.debug(f"CPU Metrics: {cpu_metrics}")

        # Extract line-level profiling data
        line_profiles = self._extract_line_profiles(pr)
        
        # Clean return_value to remove non-serializable objects
        cleaned_result = None
        if result is not None:
            if isinstance(result, dict):
                # Filter out non-serializable objects from namespace
                cleaned_result = {}
                for key, value in result.items():
                    # Skip internal/private keys and non-serializable types
                    if not key.startswith('_') and not callable(value):
                        try:
                            import json
                            json.dumps(value)  # Test if serializable
                            cleaned_result[key] = value
                        except (TypeError, ValueError):
                            # Skip non-serializable values
                            pass
            else:
                cleaned_result = result

        return {
            "time": time_metrics,
            "memory": mem_metrics,
            "io": io_metrics,
            "gc": gc_metrics,
            "cpu": cpu_metrics,
            "allocations": allocation_metrics,
            "hotspots": hotspots,
            "call_tree": call_tree_data, # Return the full structure
            "return_value": cleaned_result,
            "error": error,
            "line_profiles": line_profiles
        }

    def _extract_line_profiles(self, profiler):
        """
        Extract per-line profiling data from cProfile stats.
        Returns dict mapping function names to their line-level stats.
        """
        line_data = {}
        
        try:
            stats = pstats.Stats(profiler)
            
            # Get detailed stats per function
            for func_key, (cc, nc, tt, ct, callers) in stats.stats.items():
                filename, line, func_name = func_key
                
                # Skip built-in functions and library code
                if '<' in filename or 'lib/python' in filename:
                    continue
                
                # Initialize function entry if not exists
                if func_name not in line_data:
                    line_data[func_name] = {
                        "filename": filename,
                        "lines": {},
                        "total_calls": nc,
                        "total_time": tt
                    }
                
                # Store line-level data
                if func_name in line_data:
                    line_data[func_name]["lines"][str(line)] = {
                        "hits": nc,
                        "total_time": round(tt * 1000, 3),  # Convert to ms
                        "time_per_hit": round((tt / nc * 1000) if nc > 0 else 0, 3)
                    }
        
        except Exception as e:
            logger.error(f"Failed to extract line profiles: {e}")
            return {}
        
        return line_data

    def _parse_hotspots(self, output: str) -> List[str]:
        lines = output.strip().split('\n')
        hotspots = []
        in_data_section = False

        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue

            # Start collecting after header (look for the column separator line)
            if '---' in line or 'ncalls' in line.lower():
                in_data_section = True
                continue

            # Collect data lines (they typically start with numbers or spaces followed by numbers)
            if in_data_section and line.strip():
                hotspots.append(line.strip())

        return hotspots[:10]  # Return top 10 hotspots
