import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from code.profiler.repo_fetcher import RepoFetcher

def test_is_url():
    fetcher = RepoFetcher()
    assert fetcher._is_url("https://github.com/user/repo.git")
    assert fetcher._is_url("git@github.com:user/repo.git")
    assert not fetcher._is_url("/local/path/to/repo")

@patch('code.profiler.repo_fetcher.git.Repo.clone_from')
def test_fetch_repo_url(mock_clone):
    fetcher = RepoFetcher()
    url = "https://github.com/user/repo.git"
    
    with patch('code.profiler.repo_fetcher.tempfile.mkdtemp', return_value="/tmp/mock_repo"):
        path = fetcher.fetch(url)
        
        assert path == "/tmp/mock_repo"
        mock_clone.assert_called_once_with(url, "/tmp/mock_repo")

def test_fetch_repo_local():
    fetcher = RepoFetcher()
    # Create a dummy local dir
    with tempfile.TemporaryDirectory() as tmpdir:
        path = fetcher.fetch(tmpdir)
        assert path == tmpdir

def test_fetch_repo_invalid_local():
    fetcher = RepoFetcher()
    with pytest.raises(ValueError):
        fetcher.fetch("/non/existent/path")
