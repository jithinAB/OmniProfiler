import pytest
import time
from unittest.mock import patch, MagicMock
from code.profiler.metrics.time_metrics import TimeCollector
from code.profiler.metrics.memory_metrics import MemoryCollector
from code.profiler.metrics.io_metrics import IOCollector

# --- Time Collector Tests ---
def test_time_collector_basic():
    collector = TimeCollector()
    with collector:
        time.sleep(0.1)
    
    metrics = collector.get_metrics()
    assert metrics['wall_time'] >= 0.1
    assert 'cpu_time' in metrics

# --- Memory Collector Tests ---
@patch('code.profiler.metrics.memory_metrics.tracemalloc')
def test_memory_collector(mock_tracemalloc):
    mock_tracemalloc.get_traced_memory.return_value = (1024, 2048)
    
    collector = MemoryCollector()
    with collector:
        pass
        
    metrics = collector.get_metrics()
    assert metrics['current_memory'] == 1024
    assert metrics['peak_memory'] == 2048
    mock_tracemalloc.start.assert_called_once()
    mock_tracemalloc.stop.assert_called_once()

# --- I/O Collector Tests ---
@patch('code.profiler.metrics.io_metrics.psutil.Process')
def test_io_collector(mock_process_cls):
    mock_proc = MagicMock()
    # Initial counters
    mock_proc.io_counters.side_effect = [
        MagicMock(read_bytes=100, write_bytes=100), # Start
        MagicMock(read_bytes=200, write_bytes=150)  # End
    ]
    mock_process_cls.return_value = mock_proc
    
    collector = IOCollector()
    with collector:
        pass
        
    metrics = collector.get_metrics()
    assert metrics['read_bytes'] == 100
    assert metrics['write_bytes'] == 50
