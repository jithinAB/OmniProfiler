#!/usr/bin/env python3
"""
Complete End-to-End Automated Profiling Example

This example demonstrates the full automated profiling workflow:
1. Generate realistic workloads at multiple scales
2. Profile code with different algorithms
3. Compare performance across scales
4. Analyze results and generate reports

Run this example:
    python examples/automated_profiling_example.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'code'))

from profiler.orchestrator import ProfileOrchestrator
from profiler.workloads import WorkloadGenerator, Benchmarks, RealisticDataGenerator
import json
from datetime import datetime


def example_1_basic_workload_generation():
    """Example 1: Generate workloads at different scales"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Workload Generation")
    print("="*70)

    generator = WorkloadGenerator()

    # Generate different types of data at different scales
    print("\n1. Integer lists:")
    for scale in ['small', 'medium']:
        data = generator.generate_list(scale=scale, randomize=True)
        print(f"   {scale}: {len(data)} elements, sample: {data[:5]}")

    print("\n2. String lists:")
    strings = generator.generate_strings(scale='small', str_length=10)
    print(f"   Generated {len(strings)} strings, sample: {strings[:3]}")

    print("\n3. Dictionary lists:")
    dict_list = generator.generate_dict_list(scale='small', num_fields=3)
    print(f"   Generated {len(dict_list)} dicts, sample: {dict_list[0]}")

    print("\n4. Matrix:")
    matrix = generator.generate_matrix(scale='small')
    print(f"   Generated {len(matrix)}x{len(matrix[0])} matrix")


def example_2_realistic_data_generation():
    """Example 2: Generate production-like realistic data"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Realistic Data Generation")
    print("="*70)

    generator = RealisticDataGenerator(seed=42)  # Reproducible data

    # E-commerce orders
    print("\n1. E-commerce orders:")
    orders = generator.generate_ecommerce_orders(scale='small')
    print(f"   Generated {len(orders)} orders")
    print(f"   Sample order: {json.dumps(orders[0], indent=2, default=str)[:300]}...")

    # User records
    print("\n2. User records:")
    users = generator.generate_user_records(scale='small', include_pii=False)
    print(f"   Generated {len(users)} users")
    print(f"   Sample user: {users[0]}")

    # API requests
    print("\n3. API requests:")
    requests = generator.generate_api_requests(scale='small')
    print(f"   Generated {len(requests)} API requests")
    print(f"   Sample request: {requests[0]}")

    # Log entries
    print("\n4. Log entries:")
    logs = generator.generate_log_entries(scale='small', log_type='application')
    print(f"   Generated {len(logs)} log entries")
    print(f"   Sample log: {logs[0]}")


def example_3_benchmark_profiling():
    """Example 3: Profile benchmark algorithms"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Benchmark Algorithm Profiling")
    print("="*70)

    orchestrator = ProfileOrchestrator()
    generator = WorkloadGenerator()

    # Test different algorithms at same scale
    scale = 'small'
    data = generator.generate_list(scale=scale, randomize=True)

    benchmarks = {
        'linear_sum': 'Benchmarks.linear_sum(_data)',
        'merge_sort': 'Benchmarks.merge_sort(_data)',
        'bubble_sort': 'Benchmarks.bubble_sort(_data)',
    }

    results = {}
    for bench_name, bench_code in benchmarks.items():
        print(f"\nProfiling {bench_name}...")

        code = f"""
from profiler.workloads import Benchmarks

_data = {repr(data)}
result = {bench_code}
"""

        try:
            result = orchestrator.profile_code(code=code, timeout_seconds=30)
            wall_time = result.get('dynamic_analysis', {}).get('time', {}).get('wall_time', 0)
            results[bench_name] = wall_time
            print(f"   Completed in {wall_time:.4f}s")
        except Exception as e:
            print(f"   Failed: {e}")

    # Compare results
    print("\n" + "-"*70)
    print("PERFORMANCE COMPARISON:")
    print(f"{'Algorithm':<20} {'Time (s)':<15}")
    print("-"*70)
    for bench_name, wall_time in sorted(results.items(), key=lambda x: x[1]):
        print(f"{bench_name:<20} {wall_time:<15.4f}")


def example_4_scaling_analysis():
    """Example 4: Analyze how algorithms scale with data size"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Scaling Analysis")
    print("="*70)

    orchestrator = ProfileOrchestrator()
    generator = WorkloadGenerator()

    # Test merge_sort across different scales
    algorithm = 'merge_sort'
    scales = ['small', 'medium']  # Add 'large' if you have time

    print(f"\nTesting {algorithm} across scales: {scales}\n")
    print(f"{'Scale':<15} {'Data Size':<15} {'Time (s)':<15} {'Memory (MB)':<15}")
    print("-"*70)

    for scale in scales:
        data = generator.generate_list(scale=scale, randomize=True)

        code = f"""
from profiler.workloads import Benchmarks

_data = {repr(data)}
result = Benchmarks.merge_sort(_data)
"""

        try:
            result = orchestrator.profile_code(code=code, timeout_seconds=60)

            wall_time = result.get('dynamic_analysis', {}).get('time', {}).get('wall_time', 0)
            peak_mem = result.get('dynamic_analysis', {}).get('memory', {}).get('peak_memory', 0)
            peak_mem_mb = peak_mem / 1024 / 1024

            print(f"{scale:<15} {len(data):<15} {wall_time:<15.4f} {peak_mem_mb:<15.2f}")

        except Exception as e:
            print(f"{scale:<15} {len(data):<15} ERROR: {e}")


def example_5_realistic_workload_profiling():
    """Example 5: Profile realistic production-like workloads"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Realistic Workload Profiling")
    print("="*70)

    orchestrator = ProfileOrchestrator()
    generator = RealisticDataGenerator(seed=42)

    # Profile e-commerce order processing
    print("\nProfiling e-commerce order processing...")
    orders = generator.generate_ecommerce_orders(scale='small')

    code = f"""
_orders = {repr(orders)}

# Simulate realistic order processing
total_revenue = 0
high_value_orders = []
customer_totals = {{}}

for order in _orders:
    # Calculate revenue
    total_revenue += order['total']

    # Track high-value orders
    if order['total'] > 500:
        high_value_orders.append(order)

    # Aggregate by customer
    customer_id = order['customer_id']
    if customer_id not in customer_totals:
        customer_totals[customer_id] = 0
    customer_totals[customer_id] += order['total']

# Find top customers
top_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:10]

result = {{
    'total_revenue': total_revenue,
    'total_orders': len(_orders),
    'high_value_orders': len(high_value_orders),
    'unique_customers': len(customer_totals),
    'avg_order_value': total_revenue / len(_orders),
    'top_customers': top_customers
}}
"""

    try:
        result = orchestrator.profile_code(code=code, timeout_seconds=30)

        print(f"   Orders processed: {len(orders)}")
        print(f"   Execution time: {result.get('dynamic_analysis', {}).get('time', {}).get('wall_time', 0):.4f}s")
        print(f"   Peak memory: {result.get('dynamic_analysis', {}).get('memory', {}).get('peak_memory', 0) / 1024 / 1024:.2f} MB")

        # Show hotspots
        hotspots = result.get('dynamic_analysis', {}).get('hotspots', [])
        if hotspots:
            print("\n   Top hotspots:")
            for i, hotspot in enumerate(hotspots[:3], 1):
                print(f"      {i}. {hotspot.get('function', 'unknown')}: "
                      f"{hotspot.get('cumtime_percent', 0):.1f}% cumulative time")

    except Exception as e:
        print(f"   Failed: {e}")


def example_6_full_automation_workflow():
    """Example 6: Complete automated profiling workflow"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Full Automation Workflow")
    print("="*70)

    # This example shows how you would typically use the automation tools
    print("\nComplete workflow includes:")
    print("1. Generate workloads at multiple scales")
    print("2. Profile with different algorithms")
    print("3. Collect and save results")
    print("4. Generate comparison reports")
    print("5. Check for performance regressions")
    print()
    print("For the full automation, use:")
    print("  python scripts/automated_profiling.py --benchmarks --scales small,medium")
    print("  python scripts/api_automation.py --api-url http://localhost:8000 --benchmarks")
    print("  python scripts/check_regression.py --baseline baseline.json --current results.json")
    print()
    print("See the scripts/ directory for complete automation tools.")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  OMNIPROFILER - AUTOMATED PROFILING EXAMPLES".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    examples = [
        ("Basic Workload Generation", example_1_basic_workload_generation),
        ("Realistic Data Generation", example_2_realistic_data_generation),
        ("Benchmark Profiling", example_3_benchmark_profiling),
        ("Scaling Analysis", example_4_scaling_analysis),
        ("Realistic Workload Profiling", example_5_realistic_workload_profiling),
        ("Full Automation Workflow", example_6_full_automation_workflow),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...\n")

    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n⚠️  Example '{name}' failed: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print("EXAMPLES COMPLETED")
    print("="*70)
    print("\nNext steps:")
    print("  - Explore the workload generators in code/profiler/workloads/")
    print("  - Try the automation scripts in scripts/")
    print("  - Start the API: cd code && uvicorn api.main:app --reload")
    print("  - Start the UI: cd ui && npm run dev")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nFailed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
