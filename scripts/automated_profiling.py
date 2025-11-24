#!/usr/bin/env python3
"""
Automated Profiling Pipeline

End-to-end automation for profiling Python code with realistic workloads.

Usage:
    python scripts/automated_profiling.py --target my_script.py --scales small,medium
    python scripts/automated_profiling.py --benchmark all --output results/
    python scripts/automated_profiling.py --config config.json
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'code'))

from profiler.orchestrator import ProfileOrchestrator
from profiler.workloads import WorkloadGenerator, Benchmarks, RealisticDataGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomatedProfilingPipeline:
    """Orchestrates automated profiling with workload generation"""

    def __init__(self, output_dir: str = 'results'):
        """
        Initialize the pipeline.

        Args:
            output_dir: Directory to save profiling results
        """
        self.orchestrator = ProfileOrchestrator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.results = []

    def profile_with_workload(self,
                             code: str,
                             workload_name: str,
                             workload_data: Any,
                             scale: str,
                             timeout_seconds: int = 30) -> Dict[str, Any]:
        """
        Profile code with a specific workload.

        Args:
            code: Python code to profile
            workload_name: Name of the workload
            workload_data: Data to inject into code
            scale: Workload scale (small/medium/large/xlarge)
            timeout_seconds: Execution timeout

        Returns:
            Profiling results dictionary
        """
        logger.info(f"Profiling {workload_name} at scale '{scale}'...")

        # Inject workload into code
        # Add data as a global variable
        full_code = f"""
# Generated workload data
_workload_data = {repr(workload_data)}

# Original code
{code}
"""

        try:
            result = self.orchestrator.profile_code(
                code=full_code,
                timeout_seconds=timeout_seconds
            )

            # Add metadata
            result['workload'] = {
                'name': workload_name,
                'scale': scale,
                'data_size': len(workload_data) if hasattr(workload_data, '__len__') else None
            }
            result['timestamp'] = datetime.now().isoformat()

            return result

        except Exception as e:
            logger.error(f"Failed to profile {workload_name}: {e}")
            return {
                'error': str(e),
                'workload': {'name': workload_name, 'scale': scale},
                'timestamp': datetime.now().isoformat()
            }

    def run_benchmark_suite(self,
                           scales: List[str] = ['small', 'medium'],
                           benchmarks: Optional[List[str]] = None,
                           timeout_seconds: int = 60) -> List[Dict[str, Any]]:
        """
        Run the full benchmark suite at different scales.

        Args:
            scales: List of scales to test ('small', 'medium', 'large', 'xlarge')
            benchmarks: Specific benchmarks to run (None = all)
            timeout_seconds: Timeout per benchmark

        Returns:
            List of profiling results
        """
        logger.info(f"Running benchmark suite at scales: {scales}")

        all_benchmarks = {
            'linear_sum': 'Benchmarks.linear_sum(_workload_data)',
            'linear_search': 'Benchmarks.linear_search(_workload_data, target=500)',
            'linear_filter': 'Benchmarks.linear_filter(_workload_data, threshold=500)',
            'merge_sort': 'Benchmarks.merge_sort(_workload_data)',
            'quicksort': 'Benchmarks.quicksort(_workload_data)',
            'bubble_sort': 'Benchmarks.bubble_sort(_workload_data)',
            'nested_loop_sum': 'Benchmarks.nested_loop_sum(_workload_data[:100])',  # Limit for O(n²)
            'cpu_intensive': 'Benchmarks.cpu_intensive_computation(_workload_data[:1000])',
            'mixed_workload': 'Benchmarks.mixed_workload(_workload_data)'
        }

        # Filter benchmarks if specified
        if benchmarks:
            all_benchmarks = {k: v for k, v in all_benchmarks.items() if k in benchmarks}

        results = []
        generator = WorkloadGenerator()

        for scale in scales:
            logger.info(f"  Testing scale: {scale}")

            # Generate workload
            data = generator.generate_list(scale=scale, randomize=True)

            for bench_name, bench_code in all_benchmarks.items():
                # Skip expensive benchmarks at large scales
                if scale in ['large', 'xlarge'] and bench_name in ['bubble_sort', 'nested_loop_sum']:
                    logger.warning(f"    Skipping {bench_name} at scale {scale} (too expensive)")
                    continue

                code = f"""
from profiler.workloads import Benchmarks

result = {bench_code}
"""
                result = self.profile_with_workload(
                    code=code,
                    workload_name=bench_name,
                    workload_data=data,
                    scale=scale,
                    timeout_seconds=timeout_seconds
                )
                results.append(result)
                self.results.append(result)

        return results

    def run_realistic_workload_suite(self,
                                    scales: List[str] = ['small', 'medium'],
                                    workload_types: Optional[List[str]] = None,
                                    timeout_seconds: int = 60) -> List[Dict[str, Any]]:
        """
        Run profiling with realistic production-like data.

        Args:
            scales: List of scales to test
            workload_types: Specific workloads to run (None = all)
            timeout_seconds: Timeout per workload

        Returns:
            List of profiling results
        """
        logger.info(f"Running realistic workload suite at scales: {scales}")

        all_workloads = {
            'ecommerce_processing': '''
from profiler.workloads import RealisticDataGenerator
gen = RealisticDataGenerator()

# Simulate order processing
total_revenue = 0
high_value_orders = []
for order in _workload_data:
    total_revenue += order['total']
    if order['total'] > 500:
        high_value_orders.append(order)

result = {
    'total_revenue': total_revenue,
    'high_value_count': len(high_value_orders),
    'avg_order_value': total_revenue / len(_workload_data)
}
''',
            'user_analysis': '''
# Simulate user analytics
active_users = [u for u in _workload_data if u['is_active']]
premium_users = [u for u in _workload_data if u.get('role') == 'premium']

result = {
    'total_users': len(_workload_data),
    'active_users': len(active_users),
    'premium_users': len(premium_users),
    'activation_rate': len(active_users) / len(_workload_data) * 100
}
''',
            'log_processing': '''
# Simulate log analysis
errors = [log for log in _workload_data if log['level'] in ['ERROR', 'CRITICAL']]
warnings = [log for log in _workload_data if log['level'] == 'WARNING']

# Group by logger
logger_counts = {}
for log in _workload_data:
    logger_name = log['logger']
    logger_counts[logger_name] = logger_counts.get(logger_name, 0) + 1

result = {
    'total_logs': len(_workload_data),
    'errors': len(errors),
    'warnings': len(warnings),
    'unique_loggers': len(logger_counts)
}
''',
            'api_analytics': '''
# Simulate API analytics
successful = [req for req in _workload_data if 200 <= req['status_code'] < 300]
errors_4xx = [req for req in _workload_data if 400 <= req['status_code'] < 500]
errors_5xx = [req for req in _workload_data if 500 <= req['status_code'] < 600]

avg_response_time = sum(req['response_time_ms'] for req in _workload_data) / len(_workload_data)

result = {
    'total_requests': len(_workload_data),
    'success_rate': len(successful) / len(_workload_data) * 100,
    'error_4xx': len(errors_4xx),
    'error_5xx': len(errors_5xx),
    'avg_response_time_ms': avg_response_time
}
'''
        }

        # Filter workloads if specified
        if workload_types:
            all_workloads = {k: v for k, v in all_workloads.items() if k in workload_types}

        results = []
        generator = RealisticDataGenerator()

        for scale in scales:
            logger.info(f"  Testing scale: {scale}")

            # Generate different workload types
            workload_data_map = {
                'ecommerce_processing': generator.generate_ecommerce_orders(scale),
                'user_analysis': generator.generate_user_records(scale),
                'log_processing': generator.generate_log_entries(scale),
                'api_analytics': generator.generate_api_requests(scale)
            }

            for workload_name, workload_code in all_workloads.items():
                data = workload_data_map[workload_name]

                result = self.profile_with_workload(
                    code=workload_code,
                    workload_name=workload_name,
                    workload_data=data,
                    scale=scale,
                    timeout_seconds=timeout_seconds
                )
                results.append(result)
                self.results.append(result)

        return results

    def save_results(self, filename: Optional[str] = None) -> Path:
        """
        Save profiling results to JSON file.

        Args:
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'profiling_results_{timestamp}.json'

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to: {output_path}")
        return output_path

    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate summary statistics from profiling results.

        Returns:
            Summary report dictionary
        """
        if not self.results:
            return {'error': 'No results available'}

        total_runs = len(self.results)
        successful_runs = len([r for r in self.results if 'error' not in r])
        failed_runs = total_runs - successful_runs

        # Extract timing data
        timings = []
        for result in self.results:
            if 'error' not in result and 'dynamic_analysis' in result:
                time_metrics = result['dynamic_analysis'].get('time', {})
                workload = result.get('workload', {})
                timings.append({
                    'workload': workload.get('name', 'unknown'),
                    'scale': workload.get('scale', 'unknown'),
                    'wall_time': time_metrics.get('wall_time', 0),
                    'cpu_time': time_metrics.get('cpu_time', 0)
                })

        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'failed_runs': failed_runs,
            'success_rate': (successful_runs / total_runs * 100) if total_runs > 0 else 0,
            'timings': timings,
            'scales_tested': list(set(r.get('workload', {}).get('scale') for r in self.results if 'workload' in r))
        }

        return summary


def main():
    """Main entry point for automated profiling"""
    parser = argparse.ArgumentParser(description='Automated Profiling Pipeline')
    parser.add_argument('--target', type=str, help='Target Python file to profile')
    parser.add_argument('--scales', type=str, default='small,medium',
                       help='Comma-separated scales (small,medium,large,xlarge)')
    parser.add_argument('--benchmarks', type=str,
                       help='Comma-separated benchmark names (default: all)')
    parser.add_argument('--realistic', action='store_true',
                       help='Run realistic workload suite')
    parser.add_argument('--workload-types', type=str,
                       help='Comma-separated realistic workload types')
    parser.add_argument('--output', type=str, default='results',
                       help='Output directory for results')
    parser.add_argument('--timeout', type=int, default=60,
                       help='Timeout per profiling run (seconds)')
    parser.add_argument('--save-summary', action='store_true',
                       help='Save summary report')

    args = parser.parse_args()

    # Parse scales
    scales = [s.strip() for s in args.scales.split(',')]

    # Initialize pipeline
    pipeline = AutomatedProfilingPipeline(output_dir=args.output)

    try:
        # Run benchmark suite
        if not args.target or args.benchmarks is not None:
            benchmarks = [b.strip() for b in args.benchmarks.split(',')] if args.benchmarks else None
            logger.info("Running benchmark suite...")
            pipeline.run_benchmark_suite(
                scales=scales,
                benchmarks=benchmarks,
                timeout_seconds=args.timeout
            )

        # Run realistic workload suite
        if args.realistic:
            workload_types = [w.strip() for w in args.workload_types.split(',')] if args.workload_types else None
            logger.info("Running realistic workload suite...")
            pipeline.run_realistic_workload_suite(
                scales=scales,
                workload_types=workload_types,
                timeout_seconds=args.timeout
            )

        # Profile target file
        if args.target:
            target_path = Path(args.target)
            if not target_path.exists():
                logger.error(f"Target file not found: {args.target}")
                return 1

            logger.info(f"Profiling target file: {args.target}")
            with open(target_path, 'r') as f:
                code = f.read()

            for scale in scales:
                data = WorkloadGenerator.generate_list(scale=scale)
                result = pipeline.profile_with_workload(
                    code=code,
                    workload_name=target_path.stem,
                    workload_data=data,
                    scale=scale,
                    timeout_seconds=args.timeout
                )
                pipeline.results.append(result)

        # Save results
        pipeline.save_results()

        # Generate and display summary
        summary = pipeline.generate_summary_report()
        logger.info("\n" + "="*60)
        logger.info("SUMMARY REPORT")
        logger.info("="*60)
        logger.info(f"Total runs: {summary['total_runs']}")
        logger.info(f"Successful: {summary['successful_runs']}")
        logger.info(f"Failed: {summary['failed_runs']}")
        logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        logger.info(f"Scales tested: {', '.join(summary['scales_tested'])}")

        if args.save_summary:
            summary_path = pipeline.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            logger.info(f"Summary saved to: {summary_path}")

        return 0

    except KeyboardInterrupt:
        logger.warning("\nProfiling interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
