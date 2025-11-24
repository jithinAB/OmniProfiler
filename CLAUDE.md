# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Omni-Profiler is a comprehensive Python code profiling tool that combines hardware detection, static analysis, and dynamic profiling. It provides both a CLI and web API for analyzing Python code performance, memory usage, complexity, and structure. The project includes a React-based UI for visualizing profiling results.

## Architecture

The system follows a modular architecture with three main components:

### Backend (Python)
- **Orchestrator** (`code/profiler/orchestrator.py`): Central controller that coordinates all profiling operations
  - Initializes hardware detection, static analysis, and dynamic profiling
  - Provides `profile_function()` and `profile_file()` methods
  - For file profiling, executes code in a separate multiprocessing worker with 5s timeout
  - Returns unified report containing hardware, static, and dynamic analysis

- **Hardware Detection** (`code/profiler/hardware.py`): Detects CPU, GPU, RAM, and OS capabilities using py-cpuinfo, psutil, GPUtil, and pynvml

- **Static Analysis** (`code/profiler/static/`):
  - `complexity.py`: Calculates cyclomatic complexity and Halstead metrics using radon and AST
  - `call_graph.py`: Builds call graphs and import trees from source code

- **Dynamic Profiling** (`code/profiler/dynamic/profiler.py`):
  - Uses cProfile for execution time profiling
  - Uses tracemalloc for memory tracking
  - Uses psutil for I/O metrics
  - Captures hotspots and runtime statistics

- **Metrics** (`code/profiler/metrics/`): Data structures for time, memory, and I/O metrics

- **API** (`code/api/main.py`): FastAPI server with endpoints:
  - POST `/profile/code`: Profile raw code snippet
  - POST `/profile/file`: Profile uploaded file
  - POST `/profile/repo`: Profile entire repository (static analysis only for safety)
  - GET `/history`: Get profiling history (currently mock)

- **CLI** (`code/cli.py`): Typer-based CLI with commands:
  - `profile <path>`: Profile a .py file or repository
  - `serve`: Start the API server

- **Repo Fetcher** (`code/profiler/repo_fetcher.py`): GitPython-based utility to clone and analyze repositories

### Frontend (React + Vite)
- **Location**: `ui/` directory
- **Main App** (`ui/src/App.jsx`): Tab-based interface with Profile, Dashboard, History, Settings views
- **Components** (`ui/src/components/`):
  - `ProfilerForm.jsx`: Form to submit code/files for profiling
  - `Dashboard.jsx`: Visualizes profiling results with charts (using recharts)
  - `Layout.jsx`: Main layout with navigation
- **API Integration**: Uses axios to communicate with FastAPI backend

## Development Commands

### Backend (Python)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run tests:**
```bash
pytest
```

**Run tests with coverage:**
```bash
pytest --cov=code/profiler --cov-report=term-missing
```

**Run single test file:**
```bash
pytest tests/test_<name>.py
```

**Start API server:**
```bash
python -m code.cli serve
# Or with custom host/port:
python -m code.cli serve --host 0.0.0.0 --port 8000
```

**Profile a file via CLI:**
```bash
python -m code.cli profile path/to/script.py
```

### Frontend (React)

**Install dependencies:**
```bash
cd ui
npm install
```

**Run development server:**
```bash
cd ui
npm run dev
```

**Build for production:**
```bash
cd ui
npm run build
```

**Lint:**
```bash
cd ui
npm run lint
```

**Preview production build:**
```bash
cd ui
npm run preview
```

## Key Implementation Details

### Code Execution and Profiling
The `orchestrator.profile_file()` method executes user code directly in the main process with the following safety measures:
- Configurable timeout (default: 5 seconds) implemented in MockInput
- Captures stdout/stderr to prevent output pollution
- Handles SystemExit gracefully for scripts that call sys.exit()
- Uses configurable mock inputs for interactive scripts (can be customized via `mock_inputs` parameter)

### MockInput Configuration
The MockInput system now supports:
- Custom input sequences via the `mock_inputs` parameter
- Configurable timeout via `timeout_seconds` parameter
- Automatic input cycling (repeats last input if script requests more)
- Default sensible inputs: `["1", "10", "2", "5", "3", "100", "exit", "quit", "4"]`

### Security Considerations
**IMPORTANT**: The profiler executes arbitrary Python code. Safety measures include:
- Input validation (code size limits, file size limits)
- Execution timeout to prevent infinite loops
- Output capture to prevent information leakage
- Repository profiling uses static analysis only (no code execution)
- API endpoints include security warnings in documentation

**Use only with trusted code in secure, isolated environments.**

### Static Analysis
Uses Python's `ast` module and `radon` library to analyze code without execution. Safe to run on any code including untrusted repositories.

### API Endpoints Safety
- `/profile/code` and `/profile/file` execute code (use with caution)
- `/profile/repo` only performs static analysis to avoid executing untrusted code

## Testing

Test files are in `tests/` directory with coverage configuration in `pytest.ini`:
- `test_hardware.py` and `test_hardware_advanced.py`: Hardware detection tests
- `test_dynamic_profiler.py` and `test_dynamic_tree.py`: Dynamic profiling tests
- `test_static_analysis.py` and `test_call_graph.py`: Static analysis tests
- `test_orchestrator.py` and `test_orchestrator_advanced.py`: Integration tests
- `test_api.py`: API endpoint tests
- `test_metrics.py`: Metrics data structure tests
- `test_repo_fetcher.py`: Repository cloning tests

## Architecture Diagrams

See `docs/architecture.md` for detailed architecture diagrams and component descriptions.

## Recent Improvements and Bug Fixes

### Security Enhancements
- Added input validation for all API endpoints (code size, file size, URL format)
- Added security warnings in API documentation and responses
- Repository profiling now uses static analysis only (no code execution)
- Improved error handling to prevent information leakage

### Dependency Updates
- Replaced deprecated `pynvml` with `nvidia-ml-py` for GPU detection
- Added proper cleanup for NVML resources using try/finally blocks

### Error Handling and Logging
- Added comprehensive logging throughout the codebase
- Replaced silent exception swallowing with proper error logging
- Improved error messages and validation feedback

### Resource Management
- Fixed temp directory cleanup leak in repo fetcher
- Added tracking system for temp directories to prevent accidental deletions
- Improved file cleanup in API endpoints with proper finally blocks

### Code Quality
- Fixed hotspot parsing logic in dynamic profiler
- Improved Dashboard component error handling and data validation
- Made MockInput configurable with custom inputs and timeouts
- Fixed test assertion mismatches

### Frontend Improvements
- Added environment variable support for API URL configuration
- Created centralized API endpoints configuration
- Added `.env.example` for documentation
- Improved Vite proxy configuration

### API Improvements
- Better HTTP status codes (400 for validation, 413 for file too large, 500 for internal errors)
- Structured error responses
- Request/response validation using Pydantic
- Automatic cleanup of temp files and repositories
- Never create any md files, docs, test py files in the root folder. Add them to docs/ or tests/ folder.