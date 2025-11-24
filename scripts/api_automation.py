#!/usr/bin/env python3
"""
API Batch Profiling Client

Automates profiling via the OmniProfiler REST API for remote/distributed profiling.

Usage:
    python scripts/api_automation.py --api-url http://localhost:8000 --benchmark all
    python scripts/api_automation.py --file my_script.py --scales small,medium
    python scripts/api_automation.py --batch workloads.json
"""

import sys
import json
import argparse
import requests
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIProfilingClient:
    """Client for batch profiling via REST API"""

    def __init__(self, api_url: str = 'http://localhost:8000', timeout: int = 300):
        """
        Initialize API client.

        Args:
            api_url: Base URL of the OmniProfiler API
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.results = []

        # Check API availability
        self._check_api_health()

    def _check_api_health(self):
        """Check if API is available"""
        try:
            response = requests.get(f'{self.api_url}/', timeout=5)
            response.raise_for_status()
            logger.info(f"Connected to API at {self.api_url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to API at {self.api_url}: {e}")
            raise

    def profile_code(self, code: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Profile code via API.

        Args:
            code: Python code to profile
            metadata: Optional metadata to attach to results

        Returns:
            Profiling results
        """
        logger.info("Submitting code for profiling...")

        try:
            response = requests.post(
                f'{self.api_url}/profile/code',
                json={'code': code},
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()

            # Add metadata
            if metadata:
                result['metadata'] = metadata
            result['timestamp'] = datetime.now().isoformat()

            logger.info("✓ Profiling completed successfully")
            return result

        except requests.exceptions.Timeout:
            logger.error("✗ Profiling timed out")
            return {'error': 'timeout', 'metadata': metadata}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ API request failed: {e}")
            return {'error': str(e), 'metadata': metadata}

    def profile_file(self, file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Profile a file via API.

        Args:
            file_path: Path to Python file
            metadata: Optional metadata

        Returns:
            Profiling results
        """
        logger.info(f"Submitting file for profiling: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f, 'text/x-python')}
                response = requests.post(
                    f'{self.api_url}/profile/file',
                    files=files,
                    timeout=self.timeout
                )
                response.raise_for_status()

            result = response.json()

            # Add metadata
            if metadata:
                result['metadata'] = metadata
            result['timestamp'] = datetime.now().isoformat()

            logger.info("✓ Profiling completed successfully")
            return result

        except FileNotFoundError:
            logger.error(f"✗ File not found: {file_path}")
            return {'error': 'file_not_found', 'metadata': metadata}
        except requests.exceptions.Timeout:
            logger.error("✗ Profiling timed out")
            return {'error': 'timeout', 'metadata': metadata}
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ API request failed: {e}")
            return {'error': str(e), 'metadata': metadata}

    def batch_profile(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Run batch profiling jobs.

        Args:
            jobs: List of job specifications, each with 'type' (code/file) and 'content'

        Returns:
            List of profiling results
        """
        logger.info(f"Starting batch profiling: {len(jobs)} jobs")

        results = []
        for i, job in enumerate(jobs, 1):
            logger.info(f"\n[Job {i}/{len(jobs)}]")

            job_type = job.get('type', 'code')
            metadata = job.get('metadata', {})
            metadata['job_index'] = i

            if job_type == 'code':
                code = job.get('content', '')
                result = self.profile_code(code, metadata)
            elif job_type == 'file':
                file_path = job.get('content', '')
                result = self.profile_file(file_path, metadata)
            else:
                logger.error(f"Unknown job type: {job_type}")
                result = {'error': f'unknown_job_type: {job_type}', 'metadata': metadata}

            results.append(result)
            self.results.append(result)

            # Rate limiting
            if i < len(jobs):
                time.sleep(0.5)  # Small delay between requests

        logger.info(f"\nBatch profiling completed: {len(results)} jobs processed")
        return results

    def profile_benchmarks(self, scales: List[str] = ['small', 'medium']) -> List[Dict[str, Any]]:
        """
        Profile all built-in benchmarks at different scales via API.

        Args:
            scales: List of scales to test

        Returns:
            List of profiling results
        """
        logger.info(f"Profiling benchmarks at scales: {scales}")

        benchmarks = {
            'linear_sum': 'Benchmarks.linear_sum(_workload_data)',
            'merge_sort': 'Benchmarks.merge_sort(_workload_data)',
            'bubble_sort': 'Benchmarks.bubble_sort(_workload_data[:1000])',  # Limit size
            'mixed_workload': 'Benchmarks.mixed_workload(_workload_data[:1000])'
        }

        jobs = []
        for scale in scales:
            scale_sizes = {'small': 100, 'medium': 10000, 'large': 1000000}
            data_size = scale_sizes.get(scale, 100)

            for bench_name, bench_code in benchmarks.items():
                # Generate workload inline
                code = f"""
import random
from profiler.workloads import Benchmarks

# Generate workload
_workload_data = [random.randint(0, 1000) for _ in range({data_size})]

# Run benchmark
result = {bench_code}
"""
                jobs.append({
                    'type': 'code',
                    'content': code,
                    'metadata': {
                        'benchmark': bench_name,
                        'scale': scale,
                        'data_size': data_size
                    }
                })

        return self.batch_profile(jobs)

    def save_results(self, output_path: str):
        """
        Save all profiling results to JSON file.

        Args:
            output_path: Path to output file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to: {output_file}")

    def generate_comparison_report(self) -> Dict[str, Any]:
        """
        Generate comparison report across all profiled jobs.

        Returns:
            Comparison report dictionary
        """
        if not self.results:
            return {'error': 'No results available'}

        # Extract timing comparisons
        comparisons = []
        for result in self.results:
            if 'error' in result:
                continue

            metadata = result.get('metadata', {})
            time_metrics = result.get('dynamic_analysis', {}).get('time', {})
            mem_metrics = result.get('dynamic_analysis', {}).get('memory', {})

            comparisons.append({
                'benchmark': metadata.get('benchmark', 'unknown'),
                'scale': metadata.get('scale', 'unknown'),
                'wall_time': time_metrics.get('wall_time', 0),
                'cpu_time': time_metrics.get('cpu_time', 0),
                'peak_memory_mb': mem_metrics.get('peak_memory', 0) / 1024 / 1024
            })

        # Group by benchmark
        by_benchmark = {}
        for comp in comparisons:
            bench = comp['benchmark']
            if bench not in by_benchmark:
                by_benchmark[bench] = []
            by_benchmark[bench].append(comp)

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_jobs': len(self.results),
            'successful_jobs': len(comparisons),
            'failed_jobs': len(self.results) - len(comparisons),
            'by_benchmark': by_benchmark,
            'all_comparisons': comparisons
        }

        return report

    def print_summary(self):
        """Print summary of profiling results to console"""
        report = self.generate_comparison_report()

        print("\n" + "="*70)
        print("PROFILING SUMMARY")
        print("="*70)
        print(f"Total jobs: {report['total_jobs']}")
        print(f"Successful: {report['successful_jobs']}")
        print(f"Failed: {report['failed_jobs']}")
        print()

        if report['all_comparisons']:
            print("TIMING RESULTS:")
            print(f"{'Benchmark':<25} {'Scale':<10} {'Wall Time':<12} {'Memory (MB)':<12}")
            print("-"*70)
            for comp in report['all_comparisons']:
                print(f"{comp['benchmark']:<25} {comp['scale']:<10} "
                      f"{comp['wall_time']:<12.4f} {comp['peak_memory_mb']:<12.2f}")

        print("="*70)


def main():
    """Main entry point for API automation"""
    parser = argparse.ArgumentParser(description='API Batch Profiling Client')
    parser.add_argument('--api-url', type=str, default='http://localhost:8000',
                       help='OmniProfiler API URL')
    parser.add_argument('--file', type=str,
                       help='Python file to profile')
    parser.add_argument('--code', type=str,
                       help='Python code to profile')
    parser.add_argument('--benchmarks', action='store_true',
                       help='Run built-in benchmark suite')
    parser.add_argument('--scales', type=str, default='small,medium',
                       help='Comma-separated scales for benchmarks')
    parser.add_argument('--batch', type=str,
                       help='JSON file with batch job specifications')
    parser.add_argument('--output', type=str, default='results/api_results.json',
                       help='Output file for results')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Request timeout in seconds')

    args = parser.parse_args()

    try:
        # Initialize client
        client = APIProfilingClient(api_url=args.api_url, timeout=args.timeout)

        # Parse scales
        scales = [s.strip() for s in args.scales.split(',')]

        # Run benchmarks
        if args.benchmarks:
            client.profile_benchmarks(scales=scales)

        # Profile file
        if args.file:
            result = client.profile_file(args.file, metadata={'source': 'cli'})
            client.results.append(result)

        # Profile code
        if args.code:
            result = client.profile_code(args.code, metadata={'source': 'cli'})
            client.results.append(result)

        # Batch profiling
        if args.batch:
            batch_path = Path(args.batch)
            if not batch_path.exists():
                logger.error(f"Batch file not found: {args.batch}")
                return 1

            with open(batch_path, 'r') as f:
                jobs = json.load(f)

            client.batch_profile(jobs)

        # Save results
        if client.results:
            client.save_results(args.output)
            client.print_summary()
        else:
            logger.warning("No profiling jobs executed. Use --file, --code, --benchmarks, or --batch")
            return 1

        return 0

    except KeyboardInterrupt:
        logger.warning("\nProfiling interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
