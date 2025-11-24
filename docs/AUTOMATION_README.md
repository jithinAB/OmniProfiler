# OmniProfiler Automation System

> **End-to-end automation for Python performance profiling with realistic workloads**

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run example workflows
python examples/automated_profiling_example.py

# 3. Profile benchmarks automatically
python scripts/automated_profiling.py --benchmarks --scales small,medium

# 4. Analyze results
python scripts/analyze_results.py --input results/profiling_results_*.json --output analysis/

# 5. Check for performance regressions
python scripts/check_regression.py --baseline baseline.json --current results.json
```

## 📦 What's Included

### Workload Generators (`code/profiler/workloads/`)

Generate realistic test data at multiple scales:

- **`generators.py`**: Basic data (lists, dicts, matrices) - 4 scale levels (100 to 10M items)
- **`benchmarks.py`**: Pre-built algorithms (O(n), O(n²), O(n³), exponential)
- **`realistic.py`**: Production-like data (e-commerce, logs, API requests, time-series)

### Automation Scripts (`scripts/`)

Complete automation tooling:

- **`automated_profiling.py`**: Batch profiling with workload generation
- **`api_automation.py`**: Remote profiling via REST API
- **`analyze_results.py`**: Analysis and visualization with pandas/matplotlib
- **`check_regression.py`**: Performance regression detection for CI/CD

### Examples (`examples/`)

- **`automated_profiling_example.py`**: Complete walkthrough of all features

### Documentation (`docs/`)

- **`automation_guide.md`**: Comprehensive guide with best practices

## 🎯 Common Use Cases

### Use Case 1: Profile Your Code with Realistic Data

```bash
# Create a Python file to profile
cat > my_algorithm.py << 'EOF'
def process_orders(orders):
    total_revenue = sum(order['total'] for order in orders)
    high_value = [o for o in orders if o['total'] > 500]
    return {'revenue': total_revenue, 'high_value_count': len(high_value)}

# Generate realistic orders
from profiler.workloads import RealisticDataGenerator
gen = RealisticDataGenerator()
orders = gen.generate_ecommerce_orders(scale='medium')

# Process them
result = process_orders(orders)
EOF

# Profile it
python scripts/automated_profiling.py --target my_algorithm.py --scales medium,large
```

### Use Case 2: Benchmark Algorithm Performance

```bash
# Profile all built-in benchmarks at multiple scales
python scripts/automated_profiling.py \
  --benchmarks \
  --scales small,medium,large \
  --output results/

# Generate visualizations
python scripts/analyze_results.py \
  --input results/profiling_results_*.json \
  --output analysis/ \
  --plot-type all

# View report
open analysis/analysis_report.md
```

### Use Case 3: Continuous Performance Testing

```bash
# 1. Create baseline (run once)
python scripts/automated_profiling.py \
  --benchmarks \
  --scales medium \
  --output baseline/

# 2. Make code changes
# ... edit your code ...

# 3. Profile updated code
python scripts/automated_profiling.py \
  --benchmarks \
  --scales medium \
  --output current/

# 4. Check for regressions (fails with exit code 1 if found)
python scripts/check_regression.py \
  --baseline baseline/profiling_results_*.json \
  --current current/profiling_results_*.json \
  --threshold 10 \
  --report regression_report.md \
  --fail-on-regression
```

### Use Case 4: Remote Profiling via API

```bash
# Terminal 1: Start API server
cd code
uvicorn api.main:app --reload

# Terminal 2: Profile via API
python scripts/api_automation.py \
  --api-url http://localhost:8000 \
  --benchmarks \
  --scales small,medium \
  --output api_results.json
```

## 📊 Generated Outputs

### Profiling Results (JSON)

```json
{
  "workload": {"name": "merge_sort", "scale": "medium", "data_size": 10000},
  "timestamp": "2024-01-15T10:30:00",
  "dynamic_analysis": {
    "time": {"wall_time": 0.0234, "cpu_time": 0.0231},
    "memory": {"peak_memory": 1048576, "current_memory": 524288},
    "hotspots": [...]
  },
  "static_analysis": {"complexity": {...}, "call_graph": {...}}
}
```

### Analysis Reports

- **Execution Time Plot**: Bar chart comparing performance across scales
- **Memory Usage Plot**: Peak memory consumption visualization
- **Scaling Efficiency Plot**: Log-log plot showing algorithm scaling (O(n), O(n²), etc.)
- **Time-Memory Scatter**: Trade-off analysis
- **Markdown Report**: Summary statistics and complete results table

### Regression Reports

```markdown
# Performance Regression Report

## Summary
- Total Comparisons: 10
- Regressions Found: 2 ⚠️
- Improvements: 3 ✓
- Unchanged: 5

### ⚠️ PERFORMANCE REGRESSION DETECTED

## Regressions
| Identifier | Metric | Baseline | Current | Change | Change % |
|------------|--------|----------|---------|--------|----------|
| merge_sort_medium | wall_time | 0.0234 | 0.0287 | 0.0053 | 22.65% |
```

## 🔧 Configuration

### Scale Levels

| Scale | Size | Use Case |
|-------|------|----------|
| `small` | 100 | Development, unit tests |
| `medium` | 10,000 | Pre-commit checks, CI |
| `large` | 1,000,000 | Production validation |
| `xlarge` | 10,000,000 | Stress testing |

### Regression Thresholds

| Threshold | Use Case |
|-----------|----------|
| 5% | Critical performance paths |
| 10% | Standard code (default) |
| 15-20% | Experimental features |

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/performance.yml
name: Performance Tests
on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run profiling
        run: |
          python scripts/automated_profiling.py \
            --benchmarks --scales small,medium \
            --output results/

      - name: Check regressions
        run: |
          python scripts/check_regression.py \
            --baseline baseline/profiling_results_*.json \
            --current results/profiling_results_*.json \
            --threshold 10 --fail-on-regression

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: results/
```

## 📚 Documentation

- **[Automation Guide](docs/automation_guide.md)**: Comprehensive guide with examples
- **[API Documentation](http://localhost:8000/docs)**: Interactive API docs (when server is running)
- **[CLAUDE.md](CLAUDE.md)**: Architecture and implementation details
- **[Examples](examples/)**: Code examples and tutorials

## 🎓 Learning Path

1. **Start Here**: Run `python examples/automated_profiling_example.py`
2. **Generate Data**: Explore workload generators (`code/profiler/workloads/`)
3. **Automate**: Use automation scripts (`scripts/`)
4. **Analyze**: Generate reports and visualizations
5. **Integrate**: Add to CI/CD pipeline
6. **Optimize**: Use insights to improve performance

## 💡 Tips & Best Practices

### ✅ DO

- Test at multiple scales to understand scaling behavior
- Use realistic workloads that match production data
- Set appropriate regression thresholds for your use case
- Store baselines in version control
- Automate profiling in CI/CD pipelines
- Profile regularly to catch regressions early

### ❌ DON'T

- Use only small datasets (may hide scaling issues)
- Use sequential/sorted data for sorting algorithms
- Set overly strict thresholds (causes false positives)
- Profile without timeouts (can hang on exponential algorithms)
- Ignore memory consumption (focus on time only)
- Profile in development mode (use production-like settings)

## 🐛 Troubleshooting

### Timeouts

```bash
# Increase timeout for long-running profiles
python scripts/automated_profiling.py --benchmarks --timeout 300
```

### Memory Issues

```bash
# Skip expensive benchmarks at large scales
python scripts/automated_profiling.py \
  --benchmarks linear_sum,merge_sort \  # Omit bubble_sort, nested_loop_sum
  --scales large
```

### API Connection Errors

```bash
# Ensure API is running
cd code && uvicorn api.main:app --reload

# Test connection
curl http://localhost:8000/
```

## 📈 Example Output

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         OMNIPROFILER - AUTOMATED PROFILING EXAMPLES              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

==================================================================
EXAMPLE 3: Benchmark Algorithm Profiling
==================================================================

Profiling linear_sum...
   Completed in 0.0001s

Profiling merge_sort...
   Completed in 0.0234s

Profiling bubble_sort...
   Completed in 0.1456s

------------------------------------------------------------------
PERFORMANCE COMPARISON:
Algorithm            Time (s)
------------------------------------------------------------------
linear_sum           0.0001
merge_sort           0.0234
bubble_sort          0.1456
```

## 🚀 Next Steps

1. **Run Examples**: `python examples/automated_profiling_example.py`
2. **Create Baselines**: Establish performance baselines for your code
3. **Integrate CI/CD**: Add performance checks to your pipeline
4. **Monitor Trends**: Track performance over time
5. **Optimize**: Use insights to improve your code

## 🤝 Contributing

See [CLAUDE.md](CLAUDE.md) for development details and architecture.

## 📄 License

See main [README.md](README.md) for license information.

---

**Questions?** Check the [Automation Guide](docs/automation_guide.md) or open an issue.
