#!/usr/bin/env python3
"""
Performance Regression Checker

Compares current profiling results against baseline to detect performance regressions.
Useful for CI/CD pipelines to prevent performance degradation.

Usage:
    python scripts/check_regression.py --baseline baseline.json --current results.json
    python scripts/check_regression.py --baseline baseline.json --current results.json --threshold 10
    python scripts/check_regression.py --baseline baseline.json --current results.json --report report.md
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceRegressionChecker:
    """Detects performance regressions by comparing profiling results"""

    def __init__(self, threshold_percent: float = 10.0):
        """
        Initialize the checker.

        Args:
            threshold_percent: Percentage threshold for regression detection (default: 10%)
        """
        self.threshold_percent = threshold_percent
        self.regressions = []
        self.improvements = []
        self.unchanged = []

    def load_results(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load profiling results from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            List of profiling results
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Results file not found: {file_path}")

        with open(path, 'r') as f:
            data = json.load(f)

        # Handle both list of results and single result
        if isinstance(data, list):
            return data
        else:
            return [data]

    def extract_metrics(self, result: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract key performance metrics from a profiling result.

        Args:
            result: Profiling result dictionary

        Returns:
            Dictionary of metrics
        """
        if 'error' in result:
            return {}

        metrics = {}

        # Time metrics
        time_data = result.get('dynamic_analysis', {}).get('time', {})
        metrics['wall_time'] = time_data.get('wall_time', 0)
        metrics['cpu_time'] = time_data.get('cpu_time', 0)

        # Memory metrics
        mem_data = result.get('dynamic_analysis', {}).get('memory', {})
        metrics['peak_memory'] = mem_data.get('peak_memory', 0)
        metrics['current_memory'] = mem_data.get('current_memory', 0)

        # I/O metrics
        io_data = result.get('dynamic_analysis', {}).get('io', {})
        metrics['read_count'] = io_data.get('read_count', 0)
        metrics['write_count'] = io_data.get('write_count', 0)

        return metrics

    def get_identifier(self, result: Dict[str, Any]) -> str:
        """
        Get identifier for a profiling result to match baseline with current.

        Args:
            result: Profiling result

        Returns:
            Identifier string
        """
        metadata = result.get('metadata', {})
        workload = result.get('workload', {})

        # Try different identification strategies
        if 'benchmark' in metadata:
            return f"{metadata['benchmark']}_{metadata.get('scale', 'unknown')}"
        elif 'name' in workload:
            return f"{workload['name']}_{workload.get('scale', 'unknown')}"
        else:
            # Fallback to index or hash
            return f"result_{hash(json.dumps(result, sort_keys=True))}"

    def compare_metrics(self,
                       baseline_metrics: Dict[str, float],
                       current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Compare two sets of metrics and calculate changes.

        Args:
            baseline_metrics: Baseline metrics
            current_metrics: Current metrics

        Returns:
            Comparison results with changes and percentages
        """
        comparison = {}

        for metric_name in baseline_metrics.keys():
            if metric_name not in current_metrics:
                continue

            baseline_value = baseline_metrics[metric_name]
            current_value = current_metrics[metric_name]

            # Avoid division by zero
            if baseline_value == 0:
                if current_value == 0:
                    change_percent = 0
                else:
                    change_percent = float('inf')
            else:
                change_percent = ((current_value - baseline_value) / baseline_value) * 100

            comparison[metric_name] = {
                'baseline': baseline_value,
                'current': current_value,
                'change': current_value - baseline_value,
                'change_percent': change_percent,
                'regression': change_percent > self.threshold_percent
            }

        return comparison

    def check_regressions(self,
                         baseline_results: List[Dict[str, Any]],
                         current_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check for regressions between baseline and current results.

        Args:
            baseline_results: Baseline profiling results
            current_results: Current profiling results

        Returns:
            Regression analysis report
        """
        logger.info(f"Comparing {len(baseline_results)} baseline results with {len(current_results)} current results")

        # Index baseline results by identifier
        baseline_map = {}
        for result in baseline_results:
            identifier = self.get_identifier(result)
            baseline_map[identifier] = self.extract_metrics(result)

        # Compare current results against baseline
        for result in current_results:
            identifier = self.get_identifier(result)

            if identifier not in baseline_map:
                logger.warning(f"No baseline found for: {identifier}")
                continue

            baseline_metrics = baseline_map[identifier]
            current_metrics = self.extract_metrics(result)

            if not baseline_metrics or not current_metrics:
                continue

            comparison = self.compare_metrics(baseline_metrics, current_metrics)

            # Categorize result
            has_regression = any(comp.get('regression', False) for comp in comparison.values())
            has_improvement = any(
                comp.get('change_percent', 0) < -self.threshold_percent
                for comp in comparison.values()
            )

            result_summary = {
                'identifier': identifier,
                'comparison': comparison,
                'metadata': result.get('metadata', {}),
                'workload': result.get('workload', {})
            }

            if has_regression:
                self.regressions.append(result_summary)
            elif has_improvement:
                self.improvements.append(result_summary)
            else:
                self.unchanged.append(result_summary)

        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'threshold_percent': self.threshold_percent,
            'total_comparisons': len(self.regressions) + len(self.improvements) + len(self.unchanged),
            'regressions': len(self.regressions),
            'improvements': len(self.improvements),
            'unchanged': len(self.unchanged),
            'regression_details': self.regressions,
            'improvement_details': self.improvements,
            'has_regressions': len(self.regressions) > 0
        }

        return report

    def generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """
        Generate Markdown-formatted report.

        Args:
            report: Regression analysis report

        Returns:
            Markdown string
        """
        md = []
        md.append("# Performance Regression Report\n")
        md.append(f"**Generated:** {report['timestamp']}\n")
        md.append(f"**Threshold:** {report['threshold_percent']}%\n")
        md.append("")

        # Summary
        md.append("## Summary\n")
        md.append(f"- **Total Comparisons:** {report['total_comparisons']}")
        md.append(f"- **Regressions Found:** {report['regressions']} ⚠️")
        md.append(f"- **Improvements:** {report['improvements']} ✓")
        md.append(f"- **Unchanged:** {report['unchanged']}")
        md.append("")

        # Status badge
        if report['has_regressions']:
            md.append("### ⚠️ **PERFORMANCE REGRESSION DETECTED**\n")
        else:
            md.append("### ✓ **NO REGRESSIONS DETECTED**\n")

        # Regressions details
        if report['regressions'] > 0:
            md.append("## Regressions\n")
            md.append("| Identifier | Metric | Baseline | Current | Change | Change % |")
            md.append("|------------|--------|----------|---------|--------|----------|")

            for reg in report['regression_details']:
                identifier = reg['identifier']
                for metric_name, metric_data in reg['comparison'].items():
                    if metric_data.get('regression', False):
                        md.append(
                            f"| {identifier} | {metric_name} | "
                            f"{metric_data['baseline']:.4f} | {metric_data['current']:.4f} | "
                            f"{metric_data['change']:.4f} | {metric_data['change_percent']:.2f}% |"
                        )
            md.append("")

        # Improvements
        if report['improvements'] > 0:
            md.append("## Improvements\n")
            md.append("| Identifier | Metric | Baseline | Current | Change | Change % |")
            md.append("|------------|--------|----------|---------|--------|----------|")

            for imp in report['improvement_details']:
                identifier = imp['identifier']
                for metric_name, metric_data in imp['comparison'].items():
                    if metric_data.get('change_percent', 0) < -report['threshold_percent']:
                        md.append(
                            f"| {identifier} | {metric_name} | "
                            f"{metric_data['baseline']:.4f} | {metric_data['current']:.4f} | "
                            f"{metric_data['change']:.4f} | {metric_data['change_percent']:.2f}% |"
                        )
            md.append("")

        return "\n".join(md)

    def print_summary(self, report: Dict[str, Any]):
        """Print summary to console"""
        print("\n" + "="*70)
        print("PERFORMANCE REGRESSION CHECK")
        print("="*70)
        print(f"Threshold: {report['threshold_percent']}%")
        print(f"Total comparisons: {report['total_comparisons']}")
        print()

        if report['has_regressions']:
            print("⚠️  REGRESSIONS DETECTED:", report['regressions'])
        else:
            print("✓  NO REGRESSIONS DETECTED")

        print(f"   Improvements: {report['improvements']}")
        print(f"   Unchanged: {report['unchanged']}")
        print()

        # Show regression details
        if report['regressions'] > 0:
            print("REGRESSION DETAILS:")
            print(f"{'Identifier':<30} {'Metric':<15} {'Change %':<10}")
            print("-"*70)
            for reg in report['regression_details']:
                identifier = reg['identifier'][:28]
                for metric_name, metric_data in reg['comparison'].items():
                    if metric_data.get('regression', False):
                        print(f"{identifier:<30} {metric_name:<15} "
                              f"{metric_data['change_percent']:>8.2f}%")

        print("="*70)


def main():
    """Main entry point for regression checker"""
    parser = argparse.ArgumentParser(description='Performance Regression Checker')
    parser.add_argument('--baseline', type=str, required=True,
                       help='Baseline profiling results (JSON)')
    parser.add_argument('--current', type=str, required=True,
                       help='Current profiling results (JSON)')
    parser.add_argument('--threshold', type=float, default=10.0,
                       help='Regression threshold percentage (default: 10%%)')
    parser.add_argument('--report', type=str,
                       help='Output markdown report file')
    parser.add_argument('--json-output', type=str,
                       help='Output JSON report file')
    parser.add_argument('--fail-on-regression', action='store_true',
                       help='Exit with error code if regressions found')

    args = parser.parse_args()

    try:
        # Initialize checker
        checker = PerformanceRegressionChecker(threshold_percent=args.threshold)

        # Load results
        logger.info(f"Loading baseline from: {args.baseline}")
        baseline_results = checker.load_results(args.baseline)

        logger.info(f"Loading current results from: {args.current}")
        current_results = checker.load_results(args.current)

        # Check regressions
        report = checker.check_regressions(baseline_results, current_results)

        # Print summary
        checker.print_summary(report)

        # Save markdown report
        if args.report:
            md_report = checker.generate_markdown_report(report)
            report_path = Path(args.report)
            report_path.parent.mkdir(exist_ok=True, parents=True)
            with open(report_path, 'w') as f:
                f.write(md_report)
            logger.info(f"Markdown report saved to: {report_path}")

        # Save JSON report
        if args.json_output:
            json_path = Path(args.json_output)
            json_path.parent.mkdir(exist_ok=True, parents=True)
            with open(json_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"JSON report saved to: {json_path}")

        # Exit with error if regressions found and flag is set
        if args.fail_on_regression and report['has_regressions']:
            logger.error("Regressions detected! Exiting with error code.")
            return 1

        return 0

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
