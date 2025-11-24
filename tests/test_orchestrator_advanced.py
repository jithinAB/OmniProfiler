import pytest
from unittest.mock import patch, MagicMock
from code.profiler.orchestrator import Orchestrator

@patch('code.profiler.orchestrator.HardwareDetector')
@patch('code.profiler.orchestrator.ComplexityAnalyzer')
@patch('code.profiler.orchestrator.CallGraphBuilder')
@patch('code.profiler.orchestrator.DynamicProfiler')
def test_orchestrator_advanced_features(mock_dyn, mock_cg, mock_static, mock_hw):
    # Setup mocks
    mock_hw_instance = mock_hw.return_value
    mock_hw_instance.detect.return_value = MagicMock()
    
    mock_static_instance = mock_static.return_value
    mock_static_instance.analyze_complexity.return_value = {}
    mock_static_instance.analyze_halstead.return_value = {}
    
    mock_cg_instance = mock_cg.return_value
    mock_cg_instance.build.return_value = {'func': ['called_func']}
    
    mock_dyn_instance = mock_dyn.return_value
    mock_dyn_instance.profile_function.return_value = {
        'time': {},
        'call_tree': "Tree Output"
    }
    
    orchestrator = Orchestrator()
    
    def sample_func(): pass
    
    report = orchestrator.profile_function(sample_func)
    
    assert 'static_analysis' in report
    assert report['static_analysis']['call_graph'] == {'func': ['called_func']}
    assert 'dynamic_analysis' in report
    assert report['dynamic_analysis']['call_tree'] == "Tree Output"
