# Omni-Profiler Requirements

## 1. Overview
The Omni-Profiler is a comprehensive profiling system designed to analyze Python code at the function, file, and repository levels. It aims to provide deep insights into performance, resource usage, and hardware interactions.

## 2. Metrics to Capture

### 2.1 Compute Metrics
-   **Execution Time**: Wall-clock time, CPU time (user/sys).
-   **CPU Usage**: Percentage utilization, per-core usage if applicable.
-   **Instruction Counts**: (If available via hardware counters/PAPI) Instructions per cycle (IPC).
-   **Function Calls**: Number of calls, recursion depth.

### 2.2 Memory Metrics
-   **Memory Usage**: Peak memory, current memory, allocation count.
-   **Memory Bandwidth**: Estimated throughput (if measurable via benchmarks or hardware counters).
-   **Object Churn**: Rate of object creation and destruction.
-   **Leak Detection**: Potential memory leaks (unfreed objects).

### 2.3 I/O Metrics
-   **Disk I/O**: Read/Write bytes, operation counts.
-   **Network I/O**: Sent/Received bytes, packet counts.

### 2.4 Code Complexity & Static Analysis
-   **Cyclomatic Complexity**: McCabe complexity score.
-   **Maintainability Index**: Composite score of maintainability.
-   **Halstead Metrics**: Volume, difficulty, effort.
-   **Call Graph**: Visual representation of function dependencies.

### 2.5 Hardware Capabilities
-   **CPU**: Vendor (Intel, AMD, ARM), Architecture (x86_64, aarch64), Cores (Physical/Logical), SIMD Extensions (AVX, AVX2, AVX-512, NEON).
-   **GPU**: Vendor (Nvidia, AMD), Model, VRAM, Driver Version, CUDA/ROCm version.
-   **OS**: Name, Version, Kernel, System Load.

## 3. Tools & Libraries

### 3.1 Hardware Detection
-   `cpuinfo`: Detailed CPU info.
-   `psutil`: System utilization and process metrics.
-   `GPUtil` / `pynvml`: Nvidia GPU stats.
-   `platform`: Basic OS info.

### 3.2 Profiling & Analysis
-   `cProfile`: Standard Python profiler for timing.
-   `tracemalloc`: Memory allocation tracking.
-   `pyinstrument`: Statistical profiler for call stack visualization.
-   `radon`: Static analysis (complexity).
-   `scalene`: (Optional) High-performance CPU/Memory profiler (might be too heavy, but good reference).

### 3.3 Visualization
-   `rich`: Terminal output formatting.
-   `matplotlib` / `plotly`: (Optional) Generating charts for reports.

## 4. Multi-Hardware Support Strategy
-   **Abstraction Layer**: Create a `HardwareInterface` that abstracts specific vendor APIs.
-   **Graceful Degradation**: If a specific hardware component (e.g., GPU) or driver is missing, the profiler should skip those metrics without crashing.
-   **Cross-Platform Checks**: Use `platform.system()` to switch strategies for Linux/macOS/Windows (though primarily targeting *nix/macOS based on user environment).

## 5. Analysis Levels
-   **Function**: Decorator-based or explicit call wrapper.
-   **File**: Script execution wrapper.
-   **Repo**: Recursive discovery of Python files, static analysis of the whole codebase, and optional entry-point profiling.
