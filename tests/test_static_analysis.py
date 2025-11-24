import pytest
from unittest.mock import patch, MagicMock
from code.profiler.static.complexity import ComplexityAnalyzer

@patch('code.profiler.static.complexity.cc_visit')
def test_cyclomatic_complexity(mock_cc_visit):
    # Mock block
    mock_block = MagicMock()
    mock_block.name = 'factorial'
    mock_block.complexity = 2
    mock_cc_visit.return_value = [mock_block]

    code = "def factorial(n): pass"
    analyzer = ComplexityAnalyzer()
    complexity = analyzer.analyze_complexity(code)
    
    assert complexity['factorial'] == 2

@patch('code.profiler.static.complexity.h_visit')
def test_halstead_metrics(mock_h_visit):
    # Mock metrics
    mock_metrics = MagicMock()
    mock_metrics.volume = 10.5
    mock_metrics.difficulty = 2.5
    mock_metrics.effort = 26.25
    mock_h_visit.return_value = mock_metrics

    code = "a = 1 + 2"
    analyzer = ComplexityAnalyzer()
    metrics = analyzer.analyze_halstead(code)
    
    assert metrics['volume'] == 10.5
    assert metrics['difficulty'] == 2.5
