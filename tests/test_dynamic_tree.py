import pytest
from unittest.mock import patch, MagicMock
from code.profiler.dynamic.profiler import DynamicProfiler

@patch('code.profiler.dynamic.profiler.Profiler')
def test_dynamic_profiler_pyinstrument(mock_profiler_cls):
    # Mock pyinstrument Profiler
    mock_profiler = MagicMock()
    mock_profiler_cls.return_value = mock_profiler
    
    # Mock output
    mock_profiler.output_text.return_value = "Tree View Output"
    
    profiler = DynamicProfiler()
    
    def sample_func(): pass
    
    metrics = profiler.profile_function(sample_func)
    
    assert 'call_tree' in metrics
    assert metrics['call_tree'] == "Tree View Output"
    mock_profiler.start.assert_called_once()
    mock_profiler.stop.assert_called_once()
