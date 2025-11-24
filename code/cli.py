import typer
import uvicorn
import os
from rich.console import Console
from rich.table import Table
from code.profiler.orchestrator import Orchestrator
from code.profiler.repo_fetcher import RepoFetcher

app = typer.Typer()
console = Console()

@app.command()
def profile(path: str):
    """
    Profile a file or repository.
    """
    orchestrator = Orchestrator()
    fetcher = RepoFetcher()
    
    try:
        # Check if it's a repo URL or local path
        if path.endswith(".py") and os.path.exists(path):
            console.print(f"[bold green]Profiling file: {path}[/bold green]")
            report = orchestrator.profile_file(path)
            
            # Save report to JSON
            import json
            import time
            timestamp = int(time.time())
            report_filename = f"profile_report_{timestamp}.json"
            with open(report_filename, "w") as f:
                json.dump(report, f, indent=2)
            
            console.print(f"[bold green]Report saved to: {report_filename}[/bold green]")
            _print_report(report)
        else:
            # Assume repo
            console.print(f"[bold blue]Fetching repo: {path}[/bold blue]")
            repo_path = fetcher.fetch(path)
            console.print(f"Repo cloned to: {repo_path}")
            # For CLI, maybe just profile main.py or list files?
            # This is a simplified view.
            console.print("[yellow]Repo profiling in CLI is limited to fetching for now.[/yellow]")
            
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000):
    """
    Start the API server.
    """
    console.print(f"[bold green]Starting API server on {host}:{port}[/bold green]")
    uvicorn.run("code.api.main:app", host=host, port=port, reload=True)

def _print_report(report):
    # Print Hardware
    hw = report.get('hardware', {})
    table = Table(title="System Info")
    table.add_column("Component")
    table.add_column("Details")
    table.add_row("CPU", f"{hw.get('cpu_vendor', 'Unknown')} {hw.get('cpu_arch', '')} ({hw.get('cpu_cores', 0)} cores)")
    table.add_row("RAM", f"{hw.get('ram_total', 0) / (1024**3):.2f} GB")
    console.print(table)
    
    # Print Dynamic
    dyn = report.get('dynamic_analysis', {})
    time_metrics = dyn.get('time', {})
    console.print(f"\n[bold]Execution Time:[/bold] {time_metrics.get('wall_time', 0):.4f}s")

@app.command()
def compare(file_a: str, file_b: str):
    """
    Compare two profiling reports.
    """
    import json
    from code.profiler.comparator import ProfilerComparator
    
    try:
        with open(file_a, 'r') as f:
            report_a = json.load(f)
        with open(file_b, 'r') as f:
            report_b = json.load(f)
            
        comparator = ProfilerComparator()
        result = comparator.compare(report_a, report_b)
        
        _print_comparison(result, file_a, file_b)
        
    except Exception as e:
        console.print(f"[bold red]Error comparing files: {e}[/bold red]")

def _print_comparison(result, file_a, file_b):
    table = Table(title=f"Comparison: {os.path.basename(file_a)} vs {os.path.basename(file_b)}")
    table.add_column("Metric")
    table.add_column("Baseline")
    table.add_column("Comparison")
    table.add_column("Diff")
    table.add_column("Status")
    
    # Time
    _add_diff_row(table, "Wall Time", result["time"]["wall_time"], "s")
    _add_diff_row(table, "CPU Time", result["time"]["cpu_time"], "s")
    
    # Memory
    _add_diff_row(table, "Peak Memory", result["memory"]["peak_memory"], " bytes")
    
    # GC
    _add_diff_row(table, "GC Objects", result["gc"]["total_objects"], "")
    _add_diff_row(table, "GC Collections", result["gc"]["total_collections"], "")
    
    # Allocations
    _add_diff_row(table, "Allocations", result["allocations"]["total_allocations"], "")
    
    console.print(table)

def _add_diff_row(table, label, data, unit):
    baseline = f"{data['baseline']:.4f}{unit}"
    comparison = f"{data['comparison']:.4f}{unit}"
    
    diff_val = data['diff']
    pct = data['pct']
    diff_str = f"{diff_val:+.4f}{unit} ({pct:+.1f}%)"
    
    status = data['status']
    color = "white"
    if status == "improved":
        color = "green"
    elif status == "degraded":
        color = "red"
        
    table.add_row(label, baseline, comparison, diff_str, f"[{color}]{status.upper()}[/{color}]")

if __name__ == "__main__":
    app()
