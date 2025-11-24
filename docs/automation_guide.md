# OmniProfiler Automation Guide

Complete guide for automating Python performance profiling with realistic workloads.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Workload Generation](#workload-generation)
- [Automated Profiling](#automated-profiling)
- [API Batch Processing](#api-batch-processing)
- [Results Analysis](#results-analysis)
- [Regression Detection](#regression-detection)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Overview

The OmniProfiler automation system enables end-to-end profiling workflows with:

- **Realistic Workload Generation**: Production-scale data at multiple sizes
- **Automated Profiling**: Batch profiling with minimal manual intervention
- **API Integration**: Remote profiling via REST API
- **Analysis & Visualization**: Automated report generation with plots
- **Regression Detection**: Compare results against baselines

### Architecture

```
┌─────────────────────┐
│ Workload Generators │
│  - Basic (lists,    │
│    dicts, matrices) │
│  - Realistic (e-    │
│    commerce, logs)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Automation Scripts  │
│  - Batch profiling  │
│  - API client       │
│  - Analysis tools   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Profiling Engine   │
│  (ProfileOrchestra- │
│   tor + API)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Results & Reports   │
│  - JSON results     │
│  - Visualizations   │
│  - Markdown reports │
└─────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Example Workflows

```bash
# See all automation examples
python examples/automated_profiling_example.py

# Run automated benchmark suite
python scripts/automated_profiling.py --benchmarks --scales small,medium

# Analyze results
python scripts/analyze_results.py --input results/profiling_results_*.json --output analysis/
```

## Workload Generation

### Basic Workloads

Generate standard data structures at different scales:

```python
from profiler.workloads import WorkloadGenerator

gen = WorkloadGenerator()

# Integer lists
small_list = gen.generate_list(scale='small', randomize=True)      # 100 items
medium_list = gen.generate_list(scale='medium', randomize=True)    # 10,000 items
large_list = gen.generate_list(scale='large', randomize=True)      # 1,000,000 items

# Other data types
strings = gen.generate_strings(scale='medium', str_length=20)
dicts = gen.generate_dict_list(scale='small', num_fields=5)
matrix = gen.generate_matrix(scale='small')  # NxN matrix
```

**Available Scales:**
- `small`: 100 elements
- `medium`: 10,000 elements
- `large`: 1,000,000 elements
- `xlarge`: 10,000,000 elements

### Realistic Production-Like Data

Generate data that mimics real-world applications:

```python
from profiler.workloads import RealisticDataGenerator

gen = RealisticDataGenerator(seed=42)  # Reproducible data

# E-commerce
orders = gen.generate_ecommerce_orders(scale='medium')
# Each order has: customer info, items, prices, shipping address, etc.

# User records
users = gen.generate_user_records(scale='medium', include_pii=True)
# Each user has: username, email, preferences, address, etc.

# API requests
requests = gen.generate_api_requests(scale='large')
# Each request has: method, endpoint, status, response time, etc.

# Log entries
logs = gen.generate_log_entries(scale='large', log_type='application')
# Each log has: timestamp, level, message, logger, etc.

# Time-series metrics
metrics = gen.generate_timeseries_metrics(scale='medium', interval_seconds=60)
# Each metric has: CPU, memory, disk I/O, network, etc.
```

### Benchmark Algorithms

Test with pre-built algorithms of known complexity:

```python
from profiler.workloads import Benchmarks

data = [1, 2, 3, 4, 5]

# O(n) - Linear time
result = Benchmarks.linear_sum(data)
result = Benchmarks.linear_search(data, target=3)

# O(n log n) - Linearithmic
result = Benchmarks.merge_sort(data)
result = Benchmarks.quicksort(data)

# O(n²) - Quadratic
result = Benchmarks.bubble_sort(data)
result = Benchmarks.nested_loop_sum(data)

# Special workloads
result = Benchmarks.cpu_intensive_computation(data)
result = Benchmarks.memory_intensive_copy(data, num_copies=100)
result = Benchmarks.mixed_workload(data)
```

## Automated Profiling

### Command-Line Usage

```bash
# Profile all benchmarks at multiple scales
python scripts/automated_profiling.py \
  --benchmarks \
  --scales small,medium,large \
  --output results/ \
  --timeout 60

# Profile specific benchmarks only
python scripts/automated_profiling.py \
  --benchmarks \
  --scales small,medium \
  --benchmarks linear_sum,merge_sort,bubble_sort

# Profile realistic workloads
python scripts/automated_profiling.py \
  --realistic \
  --scales small,medium \
  --workload-types ecommerce_processing,log_processing

# Profile a specific file with generated workloads
python scripts/automated_profiling.py \
  --target my_script.py \
  --scales small,medium \
  --timeout 120
```

### Programmatic Usage

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd() / 'code'))

from profiler.orchestrator import ProfileOrchestrator
from profiler.workloads import WorkloadGenerator, Benchmarks

orchestrator = ProfileOrchestrator()
generator = WorkloadGenerator()

# Generate workload
data = generator.generate_list(scale='medium', randomize=True)

# Profile code with workload
code = f"""
from profiler.workloads import Benchmarks

_data = {repr(data)}
result = Benchmarks.merge_sort(_data)
"""

result = orchestrator.profile_code(code=code, timeout_seconds=30)

# Access results
print(f"Execution time: {result['dynamic_analysis']['time']['wall_time']}s")
print(f"Peak memory: {result['dynamic_analysis']['memory']['peak_memory'] / 1024 / 1024} MB")
```

## API Batch Processing

### Start the API Server

```bash
cd code
uvicorn api.main:app --reload --port 8000
```

### Profile via API

```bash
# Profile benchmarks via API
python scripts/api_automation.py \
  --api-url http://localhost:8000 \
  --benchmarks \
  --scales small,medium \
  --output results/api_results.json

# Profile a specific file
python scripts/api_automation.py \
  --api-url http://localhost:8000 \
  --file my_script.py \
  --output results/my_script_results.json

# Batch profiling from JSON config
python scripts/api_automation.py \
  --api-url http://localhost:8000 \
  --batch jobs.json \
  --output results/batch_results.json
```

### Batch Configuration Format

Create `jobs.json`:

```json
[
  {
    "type": "code",
    "content": "import time\ntime.sleep(0.1)\nresult = sum(range(1000))",
    "metadata": {
      "name": "simple_sum",
      "description": "Test basic sum operation"
    }
  },
  {
    "type": "file",
    "content": "path/to/script.py",
    "metadata": {
      "name": "my_script",
      "version": "1.0"
    }
  }
]
```

## Results Analysis

### Generate Visualizations

```bash
# Generate all plots and reports
python scripts/analyze_results.py \
  --input results/profiling_results_*.json \
  --output analysis/ \
  --plot-type all

# Generate specific plot types
python scripts/analyze_results.py \
  --input results.json \
  --plot-type time

# Export to CSV
python scripts/analyze_results.py \
  --input results.json \
  --csv data.csv
```

### Generated Outputs

The analysis script creates:

1. **execution_time.png**: Bar chart comparing execution times
2. **memory_usage.png**: Memory consumption across workloads
3. **scaling_efficiency.png**: Log-log plot showing algorithm scaling
4. **time_memory_scatter.png**: Trade-off visualization
5. **analysis_report.md**: Comprehensive markdown report
6. **data.csv**: Raw data export (optional)

### Programmatic Analysis

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'scripts'))

from analyze_results import ProfilingAnalyzer

analyzer = ProfilingAnalyzer('results/profiling_results.json')

# Get summary statistics
summary = analyzer.generate_summary_statistics()
print(summary)

# Generate plots
analyzer.plot_execution_time_comparison('time_comparison.png')
analyzer.plot_memory_usage('memory_usage.png')
analyzer.plot_scaling_efficiency('scaling.png')

# Generate report
analyzer.generate_markdown_report('report.md')
```

## Regression Detection

### Command-Line Usage

```bash
# Compare current results against baseline
python scripts/check_regression.py \
  --baseline baseline_results.json \
  --current current_results.json \
  --threshold 10 \
  --report regression_report.md \
  --fail-on-regression

# Custom threshold (15% slowdown)
python scripts/check_regression.py \
  --baseline baseline.json \
  --current current.json \
  --threshold 15
```

### CI/CD Integration

Use in GitHub Actions, GitLab CI, or Jenkins:

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run profiling
        run: |
          python scripts/automated_profiling.py \
            --benchmarks \
            --scales small,medium \
            --output results/

      - name: Check for regressions
        run: |
          python scripts/check_regression.py \
            --baseline baseline/results.json \
            --current results/profiling_results_*.json \
            --threshold 10 \
            --report regression_report.md \
            --fail-on-regression

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: regression_report.md
```

## CI/CD Integration

### Establishing Baselines

```bash
# Run initial profiling to create baseline
python scripts/automated_profiling.py \
  --benchmarks \
  --scales small,medium \
  --output baseline/

# Save this baseline in version control
git add baseline/profiling_results_*.json
git commit -m "Add performance baseline"
```

### Continuous Monitoring

```bash
#!/bin/bash
# performance_check.sh

# Run profiling
python scripts/automated_profiling.py \
  --benchmarks \
  --scales small,medium \
  --output current/

# Check for regressions
python scripts/check_regression.py \
  --baseline baseline/profiling_results_*.json \
  --current current/profiling_results_*.json \
  --threshold 10 \
  --report regression_report.md \
  --json-output regression_results.json \
  --fail-on-regression

EXIT_CODE=$?

# Generate analysis
python scripts/analyze_results.py \
  --input current/profiling_results_*.json \
  --output analysis/ \
  --plot-type all

exit $EXIT_CODE
```

## Best Practices

### 1. Choose Appropriate Scales

- **Development/Testing**: Use `small` (100 items)
- **Pre-commit Checks**: Use `small` to `medium` (100-10K items)
- **CI/CD Pipelines**: Use `medium` (10K items)
- **Production Validation**: Use `large` (1M items) or `xlarge` (10M items)

### 2. Set Realistic Thresholds

```bash
# Strict threshold for critical paths (5%)
--threshold 5

# Standard threshold for general code (10%)
--threshold 10

# Lenient threshold for experimental code (20%)
--threshold 20
```

### 3. Use Representative Workloads

```python
# Bad: Using sequential data for sorting algorithms
data = list(range(10000))  # Already sorted!

# Good: Using randomized data
data = WorkloadGenerator.generate_list(scale='medium', randomize=True)

# Better: Using realistic production data
gen = RealisticDataGenerator()
data = gen.generate_ecommerce_orders(scale='medium')
```

### 4. Profile at Multiple Scales

Always test at multiple scales to understand scaling behavior:

```bash
python scripts/automated_profiling.py \
  --benchmarks \
  --scales small,medium,large  # Test across scales
```

### 5. Automate Everything

Create a `Makefile`:

```makefile
.PHONY: profile analyze check-regression

profile:
	python scripts/automated_profiling.py \
		--benchmarks \
		--scales small,medium \
		--output results/

analyze:
	python scripts/analyze_results.py \
		--input results/profiling_results_*.json \
		--output analysis/

check-regression:
	python scripts/check_regression.py \
		--baseline baseline/profiling_results_*.json \
		--current results/profiling_results_*.json \
		--threshold 10 \
		--report regression_report.md

all: profile analyze check-regression
```

Then simply run:

```bash
make all
```

### 6. Store Baselines in Version Control

```bash
# Create baseline
python scripts/automated_profiling.py --benchmarks --scales medium --output baseline/

# Commit baseline
git add baseline/
git commit -m "Update performance baseline for v2.0"

# Tag for reference
git tag -a perf-baseline-v2.0 -m "Performance baseline for v2.0"
```

## Troubleshooting

### Timeouts

If profiling times out, increase the timeout:

```bash
python scripts/automated_profiling.py \
  --benchmarks \
  --timeout 300  # 5 minutes
```

### Memory Issues

For large-scale profiling:

```bash
# Skip expensive benchmarks at large scales
python scripts/automated_profiling.py \
  --benchmarks linear_sum,merge_sort \  # Skip bubble_sort, nested_loop_sum
  --scales large
```

### API Connection Errors

Ensure API server is running:

```bash
# Terminal 1: Start API
cd code
uvicorn api.main:app --reload

# Terminal 2: Run automation
python scripts/api_automation.py --api-url http://localhost:8000 --benchmarks
```

## Example Workflows

### Workflow 1: Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python scripts/automated_profiling.py \
  --benchmarks \
  --scales small \
  --output /tmp/profiling/

python scripts/check_regression.py \
  --baseline baseline/results.json \
  --current /tmp/profiling/profiling_results_*.json \
  --threshold 20 \
  --fail-on-regression
```

### Workflow 2: Nightly Performance Tests

```bash
#!/bin/bash
# cron: 0 2 * * * /path/to/nightly_profiling.sh

DATE=$(date +%Y%m%d)
OUTPUT_DIR="performance_history/$DATE"

# Run comprehensive profiling
python scripts/automated_profiling.py \
  --benchmarks \
  --realistic \
  --scales small,medium,large \
  --output "$OUTPUT_DIR/"

# Generate analysis
python scripts/analyze_results.py \
  --input "$OUTPUT_DIR/profiling_results_*.json" \
  --output "$OUTPUT_DIR/analysis/"

# Check regression
python scripts/check_regression.py \
  --baseline baseline/results.json \
  --current "$OUTPUT_DIR/profiling_results_*.json" \
  --report "$OUTPUT_DIR/regression_report.md"

# Email report
mail -s "Performance Report $DATE" team@example.com < "$OUTPUT_DIR/regression_report.md"
```

### Workflow 3: Pull Request Validation

```yaml
# .github/workflows/pr-performance.yml
name: PR Performance Check

on: pull_request

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for baseline

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Checkout baseline
        run: git checkout main -- baseline/

      - name: Profile current code
        run: |
          python scripts/automated_profiling.py \
            --benchmarks \
            --scales medium \
            --output current_results/

      - name: Check for regressions
        run: |
          python scripts/check_regression.py \
            --baseline baseline/profiling_results_*.json \
            --current current_results/profiling_results_*.json \
            --threshold 15 \
            --report pr_performance_report.md \
            --fail-on-regression

      - name: Comment PR
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('pr_performance_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

## Next Steps

1. **Explore Examples**: Run `python examples/automated_profiling_example.py`
2. **Create Baselines**: Establish performance baselines for your code
3. **Integrate CI/CD**: Add performance checks to your pipeline
4. **Monitor Trends**: Track performance over time
5. **Optimize**: Use insights to improve your code

## Resources

- [OmniProfiler Documentation](../README.md)
- [CLAUDE.md](../CLAUDE.md) - Architecture details
- [API Documentation](http://localhost:8000/docs) - When API is running
- [Example Workflows](../examples/)

## Support

For issues, questions, or contributions:
- GitHub Issues: [Report a problem](https://github.com/your-repo/issues)
- Documentation: [Read the docs](../README.md)
- Examples: [See examples/](../examples/)
