#!/usr/bin/env python3
"""
Profiling Results Analysis and Visualization

Analyzes profiling results and generates visualizations using pandas and matplotlib.

Usage:
    python scripts/analyze_results.py --input results.json --output analysis/
    python scripts/analyze_results.py --input results.json --plot-type all
    python scripts/analyze_results.py --input results.json --markdown report.md
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
import logging

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from tabulate import tabulate

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfilingAnalyzer:
    """Analyze and visualize profiling results"""

    def __init__(self, results_file: str):
        """
        Initialize analyzer with results file.

        Args:
            results_file: Path to JSON profiling results
        """
        self.results_file = Path(results_file)
        self.results = []
        self.df = None
        self._load_results()
        self._create_dataframe()

    def _load_results(self):
        """Load profiling results from JSON"""
        if not self.results_file.exists():
            raise FileNotFoundError(f"Results file not found: {self.results_file}")

        logger.info(f"Loading results from: {self.results_file}")
        with open(self.results_file, 'r') as f:
            data = json.load(f)

        # Handle both list and single result
        self.results = data if isinstance(data, list) else [data]
        logger.info(f"Loaded {len(self.results)} profiling results")

    def _create_dataframe(self):
        """Convert results to pandas DataFrame for analysis"""
        rows = []

        for result in self.results:
            if 'error' in result:
                continue

            # Extract metadata
            workload = result.get('workload', {})
            metadata = result.get('metadata', {})

            # Extract metrics
            time_metrics = result.get('dynamic_analysis', {}).get('time', {})
            mem_metrics = result.get('dynamic_analysis', {}).get('memory', {})
            io_metrics = result.get('dynamic_analysis', {}).get('io', {})

            row = {
                'workload_name': workload.get('name') or metadata.get('benchmark', 'unknown'),
                'scale': workload.get('scale') or metadata.get('scale', 'unknown'),
                'data_size': workload.get('data_size') or metadata.get('data_size', 0),
                'wall_time': time_metrics.get('wall_time', 0),
                'cpu_time': time_metrics.get('cpu_time', 0),
                'peak_memory_mb': mem_metrics.get('peak_memory', 0) / 1024 / 1024,
                'current_memory_mb': mem_metrics.get('current_memory', 0) / 1024 / 1024,
                'read_count': io_metrics.get('read_count', 0),
                'write_count': io_metrics.get('write_count', 0),
            }
            rows.append(row)

        self.df = pd.DataFrame(rows)
        logger.info(f"Created DataFrame with {len(self.df)} rows")

    def generate_summary_statistics(self) -> pd.DataFrame:
        """
        Generate summary statistics.

        Returns:
            DataFrame with summary stats
        """
        if self.df.empty:
            return pd.DataFrame()

        # Group by workload and scale
        summary = self.df.groupby(['workload_name', 'scale']).agg({
            'wall_time': ['mean', 'min', 'max', 'std'],
            'cpu_time': ['mean', 'min', 'max'],
            'peak_memory_mb': ['mean', 'max'],
        }).round(4)

        return summary

    def plot_execution_time_comparison(self, output_path: str):
        """
        Plot execution time comparison across workloads.

        Args:
            output_path: Path to save the plot
        """
        if self.df.empty:
            logger.warning("No data to plot")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        # Group by workload and scale
        pivot_data = self.df.pivot_table(
            values='wall_time',
            index='workload_name',
            columns='scale',
            aggfunc='mean'
        )

        pivot_data.plot(kind='bar', ax=ax)
        ax.set_title('Execution Time Comparison Across Scales', fontsize=14, fontweight='bold')
        ax.set_xlabel('Workload', fontsize=12)
        ax.set_ylabel('Wall Time (seconds)', fontsize=12)
        ax.legend(title='Scale', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved execution time plot to: {output_path}")
        plt.close()

    def plot_memory_usage(self, output_path: str):
        """
        Plot memory usage across workloads.

        Args:
            output_path: Path to save the plot
        """
        if self.df.empty:
            logger.warning("No data to plot")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        pivot_data = self.df.pivot_table(
            values='peak_memory_mb',
            index='workload_name',
            columns='scale',
            aggfunc='max'
        )

        pivot_data.plot(kind='bar', ax=ax, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'])
        ax.set_title('Peak Memory Usage Across Scales', fontsize=14, fontweight='bold')
        ax.set_xlabel('Workload', fontsize=12)
        ax.set_ylabel('Peak Memory (MB)', fontsize=12)
        ax.legend(title='Scale', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved memory usage plot to: {output_path}")
        plt.close()

    def plot_scaling_efficiency(self, output_path: str):
        """
        Plot how algorithms scale with data size.

        Args:
            output_path: Path to save the plot
        """
        if self.df.empty or 'data_size' not in self.df.columns:
            logger.warning("No scaling data to plot")
            return

        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot each workload's scaling
        for workload in self.df['workload_name'].unique():
            workload_data = self.df[self.df['workload_name'] == workload].sort_values('data_size')
            if len(workload_data) > 1:
                ax.plot(workload_data['data_size'], workload_data['wall_time'],
                       marker='o', label=workload, linewidth=2, markersize=6)

        ax.set_title('Algorithm Scaling: Time vs Data Size', fontsize=14, fontweight='bold')
        ax.set_xlabel('Data Size', fontsize=12)
        ax.set_ylabel('Wall Time (seconds)', fontsize=12)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend(fontsize=9, loc='best')
        ax.grid(True, alpha=0.3, which='both')
        plt.tight_layout()

        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved scaling efficiency plot to: {output_path}")
        plt.close()

    def plot_time_memory_scatter(self, output_path: str):
        """
        Scatter plot of time vs memory usage.

        Args:
            output_path: Path to save the plot
        """
        if self.df.empty:
            logger.warning("No data to plot")
            return

        fig, ax = plt.subplots(figsize=(10, 8))

        # Color by scale
        scales = self.df['scale'].unique()
        colors = plt.cm.viridis(range(len(scales)))
        color_map = dict(zip(scales, colors))

        for scale in scales:
            scale_data = self.df[self.df['scale'] == scale]
            ax.scatter(scale_data['wall_time'], scale_data['peak_memory_mb'],
                      label=scale, alpha=0.6, s=100, c=[color_map[scale]])

        ax.set_title('Time vs Memory Trade-off', fontsize=14, fontweight='bold')
        ax.set_xlabel('Wall Time (seconds)', fontsize=12)
        ax.set_ylabel('Peak Memory (MB)', fontsize=12)
        ax.legend(title='Scale', fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig(output_path, dpi=150)
        logger.info(f"Saved time-memory scatter plot to: {output_path}")
        plt.close()

    def generate_markdown_report(self, output_path: str):
        """
        Generate comprehensive markdown report.

        Args:
            output_path: Path to save the markdown file
        """
        md = []
        md.append("# Profiling Analysis Report\n")
        md.append(f"**Generated from:** `{self.results_file.name}`\n")
        md.append(f"**Total results:** {len(self.results)}\n")
        md.append("")

        # Summary statistics
        md.append("## Summary Statistics\n")
        if not self.df.empty:
            summary = self.generate_summary_statistics()
            md.append("```")
            md.append(summary.to_string())
            md.append("```\n")

            # Top performers
            md.append("## Top Performers\n")
            md.append("### Fastest Execution (by scale)\n")
            for scale in self.df['scale'].unique():
                scale_data = self.df[self.df['scale'] == scale].nsmallest(5, 'wall_time')
                if not scale_data.empty:
                    md.append(f"\n**{scale}:**\n")
                    md.append("| Workload | Time (s) | Memory (MB) |")
                    md.append("|----------|----------|-------------|")
                    for _, row in scale_data.iterrows():
                        md.append(f"| {row['workload_name']} | {row['wall_time']:.4f} | {row['peak_memory_mb']:.2f} |")

            # Memory efficient
            md.append("\n### Most Memory Efficient\n")
            efficient = self.df.nsmallest(10, 'peak_memory_mb')
            md.append("| Workload | Scale | Memory (MB) | Time (s) |")
            md.append("|----------|-------|-------------|----------|")
            for _, row in efficient.iterrows():
                md.append(f"| {row['workload_name']} | {row['scale']} | "
                         f"{row['peak_memory_mb']:.2f} | {row['wall_time']:.4f} |")

            # Full data table
            md.append("\n## Complete Results\n")
            table_data = self.df[['workload_name', 'scale', 'wall_time', 'cpu_time',
                                 'peak_memory_mb', 'read_count', 'write_count']]
            md.append(tabulate(table_data, headers='keys', tablefmt='github', showindex=False))
            md.append("")

        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        with open(output_file, 'w') as f:
            f.write('\n'.join(md))

        logger.info(f"Saved markdown report to: {output_file}")

    def export_csv(self, output_path: str):
        """
        Export results to CSV.

        Args:
            output_path: Path to save CSV file
        """
        if self.df.empty:
            logger.warning("No data to export")
            return

        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        self.df.to_csv(output_file, index=False)
        logger.info(f"Saved CSV to: {output_file}")


def main():
    """Main entry point for analysis tool"""
    parser = argparse.ArgumentParser(description='Profiling Results Analysis and Visualization')
    parser.add_argument('--input', type=str, required=True,
                       help='Input JSON profiling results file')
    parser.add_argument('--output', type=str, default='analysis',
                       help='Output directory for analysis results')
    parser.add_argument('--plot-type', type=str, default='all',
                       choices=['all', 'time', 'memory', 'scaling', 'scatter'],
                       help='Type of plots to generate')
    parser.add_argument('--markdown', type=str,
                       help='Generate markdown report at specified path')
    parser.add_argument('--csv', type=str,
                       help='Export data to CSV at specified path')

    args = parser.parse_args()

    try:
        # Initialize analyzer
        analyzer = ProfilingAnalyzer(args.input)

        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True, parents=True)

        # Generate plots
        if args.plot_type in ['all', 'time']:
            analyzer.plot_execution_time_comparison(str(output_dir / 'execution_time.png'))

        if args.plot_type in ['all', 'memory']:
            analyzer.plot_memory_usage(str(output_dir / 'memory_usage.png'))

        if args.plot_type in ['all', 'scaling']:
            analyzer.plot_scaling_efficiency(str(output_dir / 'scaling_efficiency.png'))

        if args.plot_type in ['all', 'scatter']:
            analyzer.plot_time_memory_scatter(str(output_dir / 'time_memory_scatter.png'))

        # Generate markdown report
        if args.markdown:
            analyzer.generate_markdown_report(args.markdown)
        else:
            analyzer.generate_markdown_report(str(output_dir / 'analysis_report.md'))

        # Export CSV
        if args.csv:
            analyzer.export_csv(args.csv)

        logger.info("\n" + "="*70)
        logger.info("ANALYSIS COMPLETED")
        logger.info("="*70)
        logger.info(f"Results saved to: {output_dir}")

        return 0

    except FileNotFoundError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
