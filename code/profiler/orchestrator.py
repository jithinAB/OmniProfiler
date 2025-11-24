import inspect
import logging
from typing import Any, Dict, Callable, Optional
from code.profiler.hardware import HardwareDetector
from code.profiler.static.complexity import ComplexityAnalyzer
from code.profiler.static.call_graph import CallGraphBuilder
from code.profiler.static.call_graph import CallGraphBuilder
from code.profiler.dynamic.profiler import DynamicProfiler
from code.profiler.dynamic.scalene_profiler import ScaleneProfiler

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Main entry point for the Omni-Profiler.
    Orchestrates hardware detection, static analysis, and dynamic profiling.
    """

    def __init__(self):
        self.hardware_detector = HardwareDetector()
        self.static_analyzer = ComplexityAnalyzer()
        self.call_graph_builder = CallGraphBuilder()
        self.call_graph_builder = CallGraphBuilder()
        self.dynamic_profiler = DynamicProfiler()
        self.scalene_profiler = ScaleneProfiler()
        self.hardware_info = self.hardware_detector.detect()

    def profile_function(self, func: Callable, *args, source_code: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Profile a single function.
        """
        # 1. Static Analysis
        try:
            if source_code:
                source = source_code
            else:
                source = inspect.getsource(func)

            complexity = self.static_analyzer.analyze_complexity(source)
            halstead = self.static_analyzer.analyze_halstead(source)
            big_o = self.static_analyzer.analyze_big_o(source)
            call_graph = self.call_graph_builder.build(source)
        except Exception as e:
            logger.error(f"Failed to perform static analysis on function: {e}")
            complexity = {}
            halstead = {}
            big_o = {}
            call_graph = {}

        # 2. Dynamic Profiling
        dynamic_results = self.dynamic_profiler.profile_function(func, *args, **kwargs)

        # 3. Aggregate Report
        return {
            "hardware": self.hardware_info.__dict__ if hasattr(self.hardware_info, '__dict__') else self.hardware_info,
            "static_analysis": {
                "complexity": complexity,
                "halstead": halstead,
                "big_o": big_o,
                "call_graph": call_graph
            },
            "dynamic_analysis": dynamic_results
        }

    def profile_file(self, file_path: str, mock_inputs: list = None, timeout_seconds: int = 5, warmup_runs: int = 0, cwd: str = None) -> Dict[str, Any]:
        """
        Profile a python script file using both standard profilers and Scalene.

        Args:
            file_path: Path to the Python file to profile
            mock_inputs: List of input values to mock for interactive scripts.
                        Defaults to generic values if None.
            timeout_seconds: Maximum execution time in seconds (default: 5)
            warmup_runs: Number of times to execute code before profiling (default: 0)
            cwd: Current working directory to execute the script in (optional)
        """
        # Read file
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {"error": f"Could not read file: {e}"}

        # Static Analysis
        complexity = self.static_analyzer.analyze_complexity(code)
        halstead = self.static_analyzer.analyze_halstead(code)
        big_o = self.static_analyzer.analyze_big_o(code)
        call_graph = self.call_graph_builder.build(code)

        # Run Scalene profiling (lightweight, statistical sampling)
        scalene_results = {}
        try:
            logger.info("Running Scalene profiling...")
            scalene_results = self.scalene_profiler.profile(
                file_path, 
                work_dir=cwd, 
                mock_inputs=mock_inputs
            )
        except Exception as e:
            logger.warning(f"Scalene profiling failed: {e}")
            scalene_results = {"error": str(e)}
        
        # Debug logging
        logger.info(f"Scalene results keys: {list(scalene_results.keys()) if scalene_results else 'None'}")
        if scalene_results and "files" in scalene_results:
            logger.info(f"Scalene has {len(scalene_results['files'])} files")
        else:
            logger.warning(f"Scalene results missing 'files' key. Keys: {list(scalene_results.keys()) if scalene_results else 'None'}")

        # Dynamic Profiling with timeout (standard profilers)
        import sys
        import io
        import time
        import tracemalloc
        import os
        from contextlib import redirect_stdout, redirect_stderr

        # Use provided inputs or sensible defaults
        if mock_inputs is None:
            mock_inputs = ["1", "10", "2", "5", "3", "100", "exit", "quit", "4"]

        # Start tracemalloc BEFORE creating the wrapper function
        # This ensures it captures allocations inside exec()
        tracemalloc_was_running = tracemalloc.is_tracing()
        if not tracemalloc_was_running:
            tracemalloc.start()

        def run_script_with_mock_input():
            """Execute script with mocked input and output capture"""

            class MockInput:
                def __init__(self, inputs_list, timeout):
                    self.inputs = inputs_list
                    self.index = 0
                    self.start_time = time.time()
                    self.timeout = timeout

                def __call__(self, prompt=""):
                    # Hard timeout check
                    elapsed = time.time() - self.start_time
                    if elapsed > self.timeout:
                        raise RuntimeError(f"Execution timeout ({self.timeout}s limit)")

                    # Cycle through inputs, repeat last one if we run out
                    if self.index < len(self.inputs):
                        val = self.inputs[self.index]
                        self.index += 1
                        return val
                    # Return the last input repeatedly
                    return self.inputs[-1] if self.inputs else "exit"

            # Capture stdout/stderr to prevent script output pollution
            captured_output = io.StringIO()
            captured_errors = io.StringIO()

            mock_input = MockInput(mock_inputs, timeout_seconds)
            namespace = {'__name__': '__main__', 'input': mock_input}

            # Handle CWD and sys.path
            original_cwd = os.getcwd()
            original_sys_path = sys.path.copy()
            
            if cwd:
                try:
                    os.chdir(cwd)
                    if cwd not in sys.path:
                        sys.path.insert(0, cwd)
                except Exception as e:
                    logger.warning(f"Failed to change CWD to {cwd}: {e}")

            with redirect_stdout(captured_output), redirect_stderr(captured_errors):
                try:
                    exec(code, namespace)
                except SystemExit:
                    # Script called sys.exit() - this is fine, just stop execution
                    pass
                except RuntimeError as e:
                    # Timeout - expected
                    if "timeout" not in str(e).lower():
                        raise
                finally:
                    # Restore CWD and sys.path
                    os.chdir(original_cwd)
                    sys.path = original_sys_path
            
            return namespace  # Return namespace to extract functions

        # Warm-up runs (if requested)
        if warmup_runs > 0:
            logger.info(f"Performing {warmup_runs} warm-up runs...")
            # Temporarily disable tracemalloc for warm-up to avoid polluting stats
            # But we need to respect if it was running globally
            
            # For warm-up, we just run the script without profiling overhead
            # We suppress output during warm-up to avoid clutter
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                for i in range(warmup_runs):
                    try:
                        # Create fresh namespace for each run
                        warmup_namespace = {'__name__': '__main__', 'input': MockInput(mock_inputs, timeout_seconds)}
                        
                        # Handle CWD for warmups too
                        original_cwd = os.getcwd()
                        original_sys_path = sys.path.copy()
                        if cwd:
                            try:
                                os.chdir(cwd)
                                if cwd not in sys.path:
                                    sys.path.insert(0, cwd)
                            except: pass

                        exec(code, warmup_namespace)
                    except (SystemExit, RuntimeError):
                        pass
                    except Exception as e:
                        logger.warning(f"Warm-up run {i+1} failed: {e}")
                    finally:
                        if cwd:
                            os.chdir(original_cwd)
                            sys.path = original_sys_path

        # Profile the execution - tracemalloc is already running
        namespace = self.dynamic_profiler.profile_function(run_script_with_mock_input)
        
        # Stop tracemalloc if we started it
        if not tracemalloc_was_running and tracemalloc.is_tracing():
            tracemalloc.stop()
        
        # Extract line-level profiling data
        line_profiles = self._profile_functions_line_level(code, namespace, timeout_seconds, mock_inputs)

        # Merge Scalene metrics into dynamic_analysis
        dynamic_analysis = {
            **namespace,
            "line_profiles": line_profiles
        }
        
        # Add Scalene-specific metrics if available
        if scalene_results and "files" in scalene_results:
            # Extract aggregated Scalene metrics
            scalene_metrics = self._extract_scalene_metrics(scalene_results)
            dynamic_analysis["scalene"] = scalene_metrics

        return {
            "hardware": self.hardware_info.__dict__ if hasattr(self.hardware_info, '__dict__') else self.hardware_info,
            "static_analysis": {
                "complexity": complexity,
                "halstead": halstead,
                "big_o": big_o,
                "call_graph": call_graph
            },
            "dynamic_analysis": dynamic_analysis,
            "scalene_analysis": scalene_results
        }
    
    def _extract_scalene_metrics(self, scalene_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and aggregate key Scalene metrics for dashboard display.
        """
        metrics = {
            "cpu_breakdown": {"python": 0, "native": 0, "system": 0},
            "memory_copy_mb_s": 0,
            "leaks": []
        }
        
        try:
            for filename, file_data in scalene_results.get("files", {}).items():
                # Aggregate CPU metrics from functions
                if "functions" in file_data:
                    for func in file_data["functions"]:
                        metrics["cpu_breakdown"]["python"] += func.get("n_cpu_percent_python", 0)
                        metrics["cpu_breakdown"]["native"] += func.get("n_cpu_percent_c", 0)
                        metrics["cpu_breakdown"]["system"] += func.get("n_sys_percent", 0)
                        metrics["memory_copy_mb_s"] += func.get("n_copy_mb_s", 0)
                
                # Collect memory leaks
                if "leaks" in file_data and file_data["leaks"]:
                    for lineno, leak_data in file_data["leaks"].items():
                        metrics["leaks"].append({
                            "file": filename,
                            "line": lineno,
                            **leak_data
                        })
        except Exception as e:
            logger.warning(f"Failed to extract Scalene metrics: {e}")
        
        return metrics
    
    
    def _profile_functions_line_level(self, code: str, namespace: dict, timeout: int, mock_inputs: list) -> dict:
        """
        Profile functions at line level using LineProfiler.
        Re-executes the code with line profiling enabled.
        """
        from code.profiler.metrics.line_profiler_collector import LineProfilerCollector
        import time
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        line_profiler = LineProfilerCollector()
        
        try:
            # Extract user-defined functions from namespace
            user_functions = []
            for name, obj in namespace.items():
                if callable(obj) and hasattr(obj, '__code__') and not name.startswith('_'):
                    # Check if it's a user-defined function (not built-in)
                    if hasattr(obj, '__module__'):
                        line_profiler.add_function(obj)
                        user_functions.append(name)
            
            if not user_functions:
                return {}
            
            # Re-execute with line profiler
            class MockInput:
                def __init__(self):
                    self.inputs = mock_inputs
                    self.index = 0
                    self.start_time = time.time()
                
                def __call__(self, prompt=""):
                    if time.time() - self.start_time > timeout:
                        raise RuntimeError(f"Execution timeout ({timeout}s)")
                    if self.index < len(self.inputs):
                        val = self.inputs[self.index]
                        self.index += 1
                        return val
                    return self.inputs[-1] if self.inputs else "exit"
            
            mock_input = MockInput()
            new_namespace = {'__name__': '__main__', 'input': mock_input}
            
            captured_output = io.StringIO()
            captured_errors = io.StringIO()
            
            line_profiler.enable()
            
            with redirect_stdout(captured_output), redirect_stderr(captured_errors):
                try:
                    exec(code, new_namespace)
                except (SystemExit, RuntimeError):
                    pass
            
            line_profiler.disable()
            
            # Extract stats
            return line_profiler.get_stats()
        
        except Exception as e:
            logger.error(f"Line profiling failed: {e}")
            return {}
