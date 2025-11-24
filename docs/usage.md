# Omni-Profiler Usage Guide

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Profiling a Function

```python
from code.profiler.orchestrator import Orchestrator

def my_function():
    # Your code here
    pass

orchestrator = Orchestrator()
report = orchestrator.profile_function(my_function)

print(report)
```

### Profiling a Script

```python
from code.profiler.orchestrator import Orchestrator

orchestrator = Orchestrator()
report = orchestrator.profile_file("path/to/script.py")

print(report)
```

## Report Structure

The returned report is a dictionary containing:

-   **hardware**: System capabilities (CPU, GPU, OS).
-   **static_analysis**:
    -   `complexity`: Cyclomatic complexity per function.
    -   `halstead`: Halstead metrics (volume, difficulty, effort).
-   **dynamic_analysis**:
    -   `time`: Wall-clock and CPU time.
    -   `memory`: Peak and current memory usage.
    -   `io`: Read/Write bytes.
    -   `hotspots`: Top CPU hotspots.
