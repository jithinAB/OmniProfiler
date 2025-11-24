# Omni-Profiler

<div align="center">

**A Comprehensive Python Code Profiling Tool**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0%2B-61DAFB.svg)](https://reactjs.org/)

*Profile your Python code with hardware detection, static analysis, and dynamic profiling - all in one tool.*

[Features](#-features) •
[Installation](#-installation) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Architecture](#-architecture)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [CLI Usage](#-cli-usage)
- [REST API](#-rest-api)
- [Web UI](#-web-ui)
- [Metrics Collected](#-metrics-collected)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

Omni-Profiler is a powerful, all-in-one Python profiling tool that combines hardware detection, static code analysis, and dynamic runtime profiling into a single unified platform. It provides insights into code performance, memory usage, complexity, and execution patterns through three interfaces: CLI, REST API, and a modern React-based web UI.

### What Makes Omni-Profiler Different?

- **🔧 Hardware-Aware**: Automatically detects and profiles against your system's CPU, GPU, RAM, and cache specifications
- **📊 Multi-Dimensional Analysis**: Combines static analysis (complexity, maintainability) with dynamic profiling (execution time, memory usage)
- **🎯 Line-Level Granularity**: Provides detailed line-by-line profiling for precise optimization
- **🌐 Multiple Interfaces**: Choose between CLI, REST API, or web UI based on your workflow
- **📈 Visual Analytics**: Interactive dashboards with charts for easy interpretation
- **⚡ Scalene Integration**: Leverages Scalene for advanced CPU/memory profiling
- **🔄 Comparison Tools**: Compare profiling reports to track performance changes

---

## ✨ Features

### Hardware Detection
- **CPU**: Vendor, architecture, cores (physical/logical), frequency, SIMD capabilities (AVX, AVX2, AVX-512)
- **Cache**: L1 (data/instruction), L2, L3 cache sizes
- **Memory**: Total RAM, type (DDR3/DDR4/DDR5), speed, channels
- **GPU**: NVIDIA/AMD GPU detection, VRAM, compute capability, utilization, temperature
- **OS**: Platform, version, kernel, architecture
- **Theoretical Performance**: GFLOPS calculations for CPU/GPU

### Static Analysis
- **Cyclomatic Complexity**: Per-function complexity scoring
- **Halstead Metrics**: Volume, difficulty, effort calculations
- **Big-O Estimation**: Algorithmic complexity based on loop nesting and recursion
- **Maintainability Index**: 0-100 scale code maintainability score
- **Raw Metrics**: LOC, SLOC, comments, blank lines
- **Call Graphs**: Function call relationships and import trees

### Dynamic Profiling
- **Time Metrics**: Wall time, CPU time, user time, system time
- **Memory Profiling**: Peak memory, current memory, tracemalloc integration
- **I/O Metrics**: Disk read/write operations and bytes
- **GC Metrics**: Garbage collection statistics per generation
- **Allocation Tracking**: Total allocations, allocation rate
- **CPU Profiling**: Hotspot detection, function-level timing
- **Line-Level Profiling**: Per-line execution time and counts
- **Scalene Integration**: Python/native CPU breakdown, memory leaks

### Interfaces
- **CLI**: Rich terminal output with tables and color coding
- **REST API**: FastAPI-based endpoints for integration
- **Web UI**: React-based dashboard with interactive visualizations

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Omni-Profiler                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │    CLI     │  │  REST API  │  │   Web UI   │    │
│  │  (Typer)   │  │ (FastAPI)  │  │  (React)   │    │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │
│        │               │               │            │
│        └───────────────┼───────────────┘            │
│                        │                            │
│              ┌─────────▼──────────┐                 │
│              │   Orchestrator     │                 │
│              │  (Coordination)    │                 │
│              └─────────┬──────────┘                 │
│                        │                            │
│        ┌───────────────┼───────────────┐            │
│        │               │               │            │
│  ┌─────▼────┐   ┌──────▼─────┐  ┌─────▼────┐      │
│  │ Hardware │   │   Static   │  │ Dynamic  │      │
│  │ Detector │   │  Analyzer  │  │ Profiler │      │
│  └──────────┘   └────────────┘  └──────────┘      │
│       │              │                 │            │
│  ┌────▼────┐   ┌─────▼──────┐   ┌─────▼──────┐    │
│  │ CPU/GPU │   │Complexity  │   │  cProfile  │    │
│  │ RAM/OS  │   │Call Graph  │   │tracemalloc │    │
│  │ Cache   │   │Halstead    │   │  Scalene   │    │
│  └─────────┘   │Radon       │   │LineProfiler│    │
│                └────────────┘   └────────────┘    │
└──────────────────────────────────────────────────────┘
```

### Component Structure

```
omni-profiler/
├── code/
│   ├── api/              # FastAPI REST API
│   │   └── main.py       # API endpoints
│   ├── cli.py            # Typer CLI interface
│   └── profiler/
│       ├── orchestrator.py      # Main coordinator
│       ├── hardware.py          # Hardware detection
│       ├── repo_fetcher.py      # Git repo handling
│       ├── comparator.py        # Report comparison
│       ├── static/              # Static analysis
│       │   ├── complexity.py    # Radon integration
│       │   └── call_graph.py    # Call graph builder
│       ├── dynamic/             # Dynamic profiling
│       │   ├── profiler.py      # cProfile/tracemalloc
│       │   └── scalene_profiler.py  # Scalene integration
│       └── metrics/             # Metric collectors
│           ├── time_metrics.py
│           ├── memory_metrics.py
│           ├── io_metrics.py
│           └── line_profiler_collector.py
├── ui/                   # React web interface
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProfilerForm.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── ComparisonView.jsx
│   │   └── App.jsx
├── tests/                # Comprehensive test suite
├── docs/                 # Additional documentation
├── scripts/              # Automation scripts
└── examples/             # Example usage
```

---

## 📦 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher (for UI)
- **Git**: For repository profiling

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/jithinAB/OmniProfiler.git
cd OmniProfiler

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -m code.cli --help
```

### Frontend Setup (Optional)

```bash
# Navigate to UI directory
cd ui

# Install dependencies
npm install

# Build for production
npm run build

# Or run development server
npm run dev
```

### Docker Setup (Coming Soon)

```bash
docker build -t omni-profiler .
docker run -p 8000:8000 omni-profiler
```

---

## 🚀 Quick Start

### 1. Profile a Python File (CLI)

```bash
python -m code.cli profile examples/sample.py
```

### 2. Start the API Server

```bash
python -m code.cli serve --host 0.0.0.0 --port 8000
```

### 3. Start the Web UI

```bash
cd ui && npm run dev
```

Navigate to `http://localhost:5173` in your browser.

### 4. Quick API Test

```bash
curl -X POST "http://localhost:8000/profile/code" \
  -H "Content-Type: application/json" \
  -d '{"code": "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)\n\nresult = fib(10)"}'
```

---

## 🖥️ CLI Usage

### Command Overview

```bash
python -m code.cli [COMMAND] [OPTIONS]
```

### Commands

#### `profile` - Profile Python Files or Repositories

Profile a single Python file:

```bash
python -m code.cli profile path/to/script.py
```

**Output**: Saves a JSON report (`profile_report_<timestamp>.json`) and displays summary in terminal.

**Features**:
- Hardware detection
- Static analysis (complexity, Halstead, Big-O)
- Dynamic profiling (execution time, memory, I/O)
- Call graph generation

#### `serve` - Start the API Server

```bash
python -m code.cli serve [OPTIONS]
```

**Options**:
- `--host TEXT`: Host address (default: `0.0.0.0`)
- `--port INTEGER`: Port number (default: `8000`)

**Example**:
```bash
python -m code.cli serve --host 127.0.0.1 --port 3000
```

#### `compare` - Compare Two Profiling Reports

```bash
python -m code.cli compare report1.json report2.json
```

**Output**: Side-by-side comparison table showing:
- Execution time differences
- Memory usage changes
- GC statistics
- Allocation metrics
- Status indicators (improved/degraded/unchanged)

**Example**:
```bash
python -m code.cli compare profile_report_1763685549.json profile_report_1763685884.json
```

---

## 🌐 REST API

The FastAPI-based REST API provides programmatic access to all profiling features.

### Base URL

```
http://localhost:8000
```

### API Documentation

Interactive API docs available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoints

#### `GET /` - Health Check

```bash
curl http://localhost:8000/
```

**Response**:
```json
{
  "status": "Omni-Profiler API is running",
  "version": "1.0.0",
  "warning": "This API executes arbitrary Python code. Use only with trusted code in secure environments."
}
```

---

#### `POST /profile/code` - Profile Code Snippet

Profile raw Python code.

**Request Body**:
```json
{
  "code": "def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n-1)\n\nresult = factorial(5)",
  "function_name": null,
  "warmup_runs": 0
}
```

**Parameters**:
- `code` (string, required): Python code to profile (max 1MB)
- `function_name` (string, optional): Specific function to profile
- `warmup_runs` (integer, optional): Number of warm-up executions before profiling (default: 0)

**Response**: Full profiling report (see [Report Structure](#report-structure))

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/profile/code" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import time\ndef slow_function():\n    time.sleep(0.1)\n    return sum(range(1000))\n\nresult = slow_function()",
    "warmup_runs": 3
  }'
```

---

#### `POST /profile/file` - Profile Uploaded File

Profile a Python file upload.

**Request**: Multipart form data with file

**Parameters**:
- `file` (file, required): `.py` file to profile (max 5MB)

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/profile/file" \
  -F "file=@path/to/script.py"
```

**Response**: Full profiling report

---

#### `POST /profile/repo` - Profile Repository

Profile an entire Git repository.

**Request Body**:
```json
{
  "url": "https://github.com/user/repo.git",
  "entry_point": "main.py"
}
```

**Parameters**:
- `url` (string, required): Git repository URL or local path
- `entry_point` (string, optional): Entry point file for dynamic profiling

**Behavior**:
- **Without `entry_point`**: Performs static analysis only on all `.py` files
- **With `entry_point`**: Adds dynamic profiling by executing the entry point

**Response**:
```json
{
  "repo_path": "/tmp/cloned_repo",
  "files": [
    {
      "path": "module/utils.py",
      "complexity": {...},
      "halstead": {...},
      "big_o": {...},
      "maintainability": 75.3,
      "call_graph": {...}
    }
  ],
  "summary": {
    "total_files": 25,
    "analyzed_files": 23,
    "failed_files": 2
  },
  "dynamic_analysis": {...}  // Only if entry_point provided
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/profile/repo" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/user/simple-project.git",
    "entry_point": "src/main.py"
  }'
```

---

#### `GET /history` - Get Profiling History

Retrieve profiling history (currently returns empty array - database integration planned).

```bash
curl http://localhost:8000/history
```

---

### Report Structure

All profiling endpoints return a comprehensive report with the following structure:

```json
{
  "hardware": {
    "cpu_vendor": "GenuineIntel",
    "cpu_brand": "Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz",
    "cpu_arch": "X86_64",
    "cpu_physical_cores": 6,
    "cpu_logical_cores": 12,
    "cpu_frequency_max": 4.5,
    "cpu_simd": ["sse", "sse2", "avx", "avx2"],
    "cache_l1_data": 32768,
    "cache_l2": 262144,
    "cache_l3": 12582912,
    "ram_total": 17179869184,
    "memory_type": "DDR4",
    "gpu_info": [...],
    "os_info": "macOS",
    "theoretical_cpu_gflops": 345.6
  },
  "static_analysis": {
    "complexity": {
      "function_name": {
        "complexity": 5,
        "lineno": 10,
        "endline": 25,
        "loc": 15
      }
    },
    "halstead": {
      "volume": 125.5,
      "difficulty": 8.3,
      "effort": 1041.65
    },
    "big_o": {
      "function_name": "O(n^2)"
    },
    "maintainability": 68.5,
    "call_graph": {...}
  },
  "dynamic_analysis": {
    "time": {
      "wall_time": 0.0523,
      "cpu_time": 0.0498,
      "user_time": 0.0456,
      "system_time": 0.0042
    },
    "memory": {
      "peak_memory": 2457600,
      "current_memory": 1843200
    },
    "io": {
      "read_count": 12,
      "write_count": 0,
      "read_bytes": 4096,
      "write_bytes": 0
    },
    "gc": {
      "generation_0": {...},
      "generation_1": {...},
      "generation_2": {...}
    },
    "allocations": {
      "total_allocations": 1250,
      "allocation_rate": 23923.5
    },
    "hotspots": [...],
    "line_profiles": {...}
  },
  "scalene_analysis": {
    "files": {...}
  }
}
```

---

## 💻 Web UI

The React-based web interface provides an intuitive visual experience for profiling.

### Starting the UI

```bash
cd ui
npm run dev
```

Access at: `http://localhost:5173`

### Configuration

Create `.env` file in `ui/` directory:

```env
VITE_API_URL=http://localhost:8000
```

### Features

#### 1. Profile Tab
- **Code Input**: Paste or type Python code
- **File Upload**: Drag-and-drop `.py` files
- **Repository URL**: Enter Git repository URL
- **Options**: Configure warmup runs, mock inputs

#### 2. Dashboard Tab
Interactive visualizations including:
- **System Information**: Hardware specs
- **Execution Metrics**: Time breakdown charts
- **Memory Analysis**: Peak/current memory graphs
- **Complexity Metrics**: Per-function complexity bars
- **Hotspots**: Top time-consuming functions
- **Line-Level Profiling**: Detailed line-by-line analysis
- **Scalene Insights**: CPU/memory breakdown

#### 3. Compare Tab
- Upload two profiling reports
- Side-by-side metric comparison
- Visual diff indicators
- Performance regression detection

#### 4. History Tab
View past profiling sessions (coming soon)

#### 5. Settings Tab
Configure profiler preferences (coming soon)

---

## 📊 Metrics Collected

### Hardware Metrics

| Category | Metrics | Tools Used |
|----------|---------|------------|
| **CPU** | Vendor, brand, architecture, cores (physical/logical), frequency (base/max), SIMD instructions (SSE, AVX, AVX-512) | py-cpuinfo, psutil |
| **Cache** | L1 data cache, L1 instruction cache, L2 cache, L3 cache (in bytes) | sysctl (macOS), lscpu (Linux), wmic (Windows) |
| **Memory** | Total RAM, memory type (DDR3/4/5), speed (MHz), channels | psutil, system_profiler (macOS), dmidecode (Linux), wmic (Windows) |
| **GPU** | Vendor, name, VRAM (total/used/free), utilization, temperature, compute capability, clock speed, driver version | nvidia-ml-py, GPUtil |
| **OS** | Platform, version, kernel, architecture | platform, subprocess |
| **Performance** | Theoretical CPU GFLOPS, theoretical GPU GFLOPS | Calculated |

### Static Analysis Metrics

| Metric | Description | Range/Format | Tool |
|--------|-------------|--------------|------|
| **Cyclomatic Complexity** | Number of linearly independent paths through code | 1-50+ (higher = more complex) | Radon |
| **Halstead Volume** | Program vocabulary and length | 0-10000+ | Radon |
| **Halstead Difficulty** | Difficulty to understand/maintain | 0-100+ | Radon |
| **Halstead Effort** | Mental effort to understand | 0-1000000+ | Radon |
| **Maintainability Index** | Overall code maintainability | 0-100 (higher = better) | Radon |
| **Big-O Complexity** | Algorithmic time complexity | O(1), O(n), O(n²), O(n³), etc. | AST analysis |
| **LOC** | Lines of code | Integer | Radon |
| **SLOC** | Source lines of code | Integer | Radon |
| **Comments** | Comment lines | Integer | Radon |
| **Call Graph** | Function call relationships | Graph structure | AST |

### Dynamic Profiling Metrics

| Metric | Description | Units | Tool |
|--------|-------------|-------|------|
| **Wall Time** | Total elapsed time | Seconds | time.perf_counter |
| **CPU Time** | Total CPU time (user + system) | Seconds | time.process_time |
| **User Time** | CPU time in user mode | Seconds | psutil |
| **System Time** | CPU time in kernel mode | Seconds | psutil |
| **Peak Memory** | Maximum memory usage | Bytes | tracemalloc |
| **Current Memory** | Memory usage at end | Bytes | tracemalloc |
| **Read Count** | Number of read operations | Integer | psutil |
| **Write Count** | Number of write operations | Integer | psutil |
| **Read Bytes** | Total bytes read | Bytes | psutil |
| **Write Bytes** | Total bytes written | Bytes | psutil |
| **GC Collections** | Garbage collections per generation | Integer | gc |
| **GC Objects** | Objects collected per generation | Integer | gc |
| **Total Allocations** | Memory allocations count | Integer | tracemalloc |
| **Allocation Rate** | Allocations per second | Allocations/s | Calculated |
| **Hotspots** | Top time-consuming functions | List | cProfile |
| **Line Profiles** | Per-line execution stats | Dict | line_profiler |
| **Python CPU %** | Python code CPU usage | Percentage | Scalene |
| **Native CPU %** | Native/C code CPU usage | Percentage | Scalene |
| **Memory Leaks** | Potential memory leaks | List | Scalene |

---

## ⚙️ Configuration

### Orchestrator Parameters

Configure profiling behavior in `orchestrator.profile_file()`:

```python
report = orchestrator.profile_file(
    file_path="script.py",
    mock_inputs=["1", "10", "exit"],      # Mock inputs for interactive scripts
    timeout_seconds=5,                     # Execution timeout
    warmup_runs=3,                         # Warm-up iterations
    cwd="/path/to/working/directory"      # Working directory
)
```

### Mock Inputs

For scripts that use `input()`, provide mock responses:

```python
# Default inputs (auto-provided)
["1", "10", "2", "5", "3", "100", "exit", "quit", "4"]

# Custom inputs
orchestrator.profile_file("interactive.py", mock_inputs=["John", "25", "yes"])
```

**Behavior**:
- Inputs are consumed in order
- Last input repeats if script requests more
- Timeout prevents infinite loops

### Environment Variables

#### Backend (API)
```bash
# .env
LOG_LEVEL=INFO
MAX_CODE_SIZE=1048576      # 1MB
MAX_FILE_SIZE=5242880      # 5MB
API_HOST=0.0.0.0
API_PORT=8000
```

#### Frontend (UI)
```bash
# ui/.env
VITE_API_URL=http://localhost:8000
```

---

## 📚 Examples

### Example 1: Profile a Recursive Function

**Code** (`fibonacci.py`):
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

result = fibonacci(20)
print(f"Fibonacci(20) = {result}")
```

**Profile**:
```bash
python -m code.cli profile fibonacci.py
```

**Key Insights**:
- High cyclomatic complexity due to recursion
- Big-O: O(2^n) - exponential time complexity
- Memory: Low peak memory (recursion stack)
- Hotspot: `fibonacci` function dominates execution time

---

### Example 2: Profile with Warm-up

**API Request**:
```python
import requests

code = """
cache = {}
def optimized_fib(n):
    if n in cache:
        return cache[n]
    if n <= 1:
        return n
    cache[n] = optimized_fib(n-1) + optimized_fib(n-2)
    return cache[n]

result = optimized_fib(30)
"""

response = requests.post(
    "http://localhost:8000/profile/code",
    json={"code": code, "warmup_runs": 5}
)

print(response.json()["dynamic_analysis"]["time"]["wall_time"])
```

---

### Example 3: Compare Two Implementations

```bash
# Profile first version
python -m code.cli profile slow_version.py
# Output: profile_report_1763685549.json

# Profile optimized version
python -m code.cli profile fast_version.py
# Output: profile_report_1763685884.json

# Compare
python -m code.cli compare profile_report_1763685549.json profile_report_1763685884.json
```

**Output**:
```
Comparison: slow_version vs fast_version
┌─────────────┬──────────┬────────────┬─────────────┬──────────┐
│ Metric      │ Baseline │ Comparison │ Diff        │ Status   │
├─────────────┼──────────┼────────────┼─────────────┼──────────┤
│ Wall Time   │ 2.4500s  │ 0.0125s    │ -2.4375s    │ IMPROVED │
│ CPU Time    │ 2.4000s  │ 0.0120s    │ -2.3880s    │ IMPROVED │
│ Peak Memory │ 1024 KB  │ 2048 KB    │ +1024 KB    │ DEGRADED │
└─────────────┴──────────┴────────────┴─────────────┴──────────┘
```

---

### Example 4: Profile a Repository

**API Request**:
```bash
curl -X POST "http://localhost:8000/profile/repo" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/yourusername/myproject.git",
    "entry_point": "src/main.py"
  }'
```

---

## 🔒 Security

### ⚠️ Important Security Warnings

**Omni-Profiler executes arbitrary Python code.** This poses significant security risks:

1. **Code Execution Risk**: Any code passed to the profiler will be executed
2. **File System Access**: Profiled code has access to the file system
3. **Network Access**: Code can make network requests
4. **Resource Consumption**: Malicious code could consume excessive resources

### Security Best Practices

#### 1. Use in Isolated Environments

```bash
# Use Docker containers
docker run --rm -it --network none omni-profiler

# Use virtual machines
# Use separate user accounts with limited permissions
```

#### 2. Trust Your Input

**Only profile code you trust completely:**
- Code you wrote yourself
- Code from verified sources
- Code reviewed by your team

**Never profile:**
- Code from untrusted sources
- User-submitted code in production
- Code from public repositories without review

#### 3. API Deployment

If deploying the API:

```python
# Add authentication
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/profile/code")
async def profile_code(request: CodeRequest, token: str = Depends(security)):
    # Verify token
    if not verify_token(token):
        raise HTTPException(status_code=401)
    # ... rest of endpoint
```

```python
# Add rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/profile/code")
@limiter.limit("5/minute")
async def profile_code(request: CodeRequest):
    # ... endpoint implementation
```

```python
# Use sandboxing
import subprocess

# Run in separate process with restricted permissions
result = subprocess.run(
    ["python", "-m", "code.profiler", "script.py"],
    capture_output=True,
    timeout=30,
    user="restricted_user"  # Unix only
)
```

#### 4. Configuration

```python
# Limit execution time
timeout_seconds = 5  # Kill execution after 5 seconds

# Limit code size
MAX_CODE_SIZE = 1024 * 1024  # 1MB limit

# Limit file size
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
```

#### 5. Repository Profiling

Repository profiling includes safety measures:

- **Static Analysis Only**: By default, repositories are only statically analyzed (no code execution)
- **Explicit Entry Point**: Dynamic profiling requires explicit `entry_point` parameter
- **Cleanup**: Cloned repositories are automatically deleted after profiling

### Security Checklist

- [ ] Run profiler in isolated environment (Docker/VM)
- [ ] Never expose API to public internet without authentication
- [ ] Use rate limiting on API endpoints
- [ ] Set reasonable timeout and size limits
- [ ] Review all code before profiling
- [ ] Monitor resource usage
- [ ] Keep dependencies updated
- [ ] Audit logs for suspicious activity

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone repository
git clone https://github.com/jithinAB/OmniProfiler.git
cd OmniProfiler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .  # Install in editable mode

# Install UI dependencies
cd ui && npm install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=code/profiler --cov-report=term-missing

# Run specific test file
pytest tests/test_orchestrator.py
```

### Code Style

- **Python**: Follow PEP 8
- **JavaScript/React**: ESLint configuration in `ui/.eslintrc.json`

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit with descriptive messages
7. Push to your fork
8. Open a Pull Request

### Reporting Issues

Use GitHub Issues to report bugs or request features. Include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Omni-Profiler builds upon excellent open-source tools:

- **[Radon](https://github.com/rubik/radon)**: Static code metrics
- **[Scalene](https://github.com/plasma-umass/scalene)**: High-performance profiler
- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern web framework
- **[Typer](https://typer.tiangolo.com/)**: CLI framework
- **[React](https://reactjs.org/)**: UI framework
- **[Recharts](https://recharts.org/)**: Charting library
- **py-cpuinfo, psutil, GPUtil**: Hardware detection libraries

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/jithinAB/OmniProfiler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jithinAB/OmniProfiler/discussions)

---

## 🗺️ Roadmap

### Upcoming Features

- [ ] Database integration for history persistence
- [ ] Advanced visualization (flame graphs, sunburst charts)
- [ ] Multi-file profiling support
- [ ] Benchmark suite generation
- [ ] CI/CD integration (GitHub Actions, GitLab CI)
- [ ] Performance regression detection
- [ ] Export formats (PDF, HTML, Markdown)
- [ ] Real-time profiling dashboard
- [ ] Docker container support
- [ ] Cloud deployment guides (AWS, GCP, Azure)

---

<div align="center">

**Made with ❤️ for the Python community**

[⭐ Star this repo](https://github.com/jithinAB/OmniProfiler) • [🐛 Report Bug](https://github.com/jithinAB/OmniProfiler/issues) • [✨ Request Feature](https://github.com/jithinAB/OmniProfiler/issues)

</div>
