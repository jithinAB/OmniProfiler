import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from code.api.main import app

client = TestClient(app)

@patch('code.api.main.orchestrator')
def test_profile_code(mock_orch):
    # The endpoint uses profile_file, not profile_function
    mock_orch.profile_file.return_value = {
        "hardware": {},
        "static_analysis": {},
        "dynamic_analysis": {}
    }

    response = client.post("/profile/code", json={
        "code": "def foo(): pass",
        "function_name": "foo"
    })

    assert response.status_code == 200
    result = response.json()
    assert "hardware" in result
    assert "static_analysis" in result
    assert "dynamic_analysis" in result

@patch('code.api.main.orchestrator')
def test_profile_file(mock_orch):
    mock_orch.profile_file.return_value = {"status": "success"}
    
    files = {'file': ('test.py', b'print("hello")', 'text/x-python')}
    response = client.post("/profile/file", files=files)
    
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

@patch('code.api.main.repo_fetcher')
@patch('code.api.main.orchestrator')
def test_profile_repo(mock_orch, mock_fetcher):
    mock_fetcher.fetch.return_value = "/tmp/mock_repo"
    
    # Mock os.walk to return one file
    with patch('code.api.main.os.walk') as mock_walk:
        mock_walk.return_value = [("/tmp/mock_repo", [], ["main.py"])]
        
        with patch('builtins.open', new_callable=MagicMock) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "def main(): pass"
            
            mock_orch.static_analyzer.analyze_complexity.return_value = {}
            mock_orch.static_analyzer.analyze_halstead.return_value = {}
            mock_orch.call_graph_builder.build.return_value = {}
            
            response = client.post("/profile/repo", json={"url": "http://github.com/user/repo"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["repo_path"] == "/tmp/mock_repo"
            assert len(data["files"]) == 1
            assert data["files"][0]["path"] == "main.py"
