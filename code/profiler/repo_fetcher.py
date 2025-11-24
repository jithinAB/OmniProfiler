import os
import tempfile
import shutil
import re
try:
    import git
except ImportError:
    git = None

class RepoFetcher:
    """Handles fetching repositories from URLs or validating local paths."""

    def __init__(self):
        # Track temp directories we create for proper cleanup
        self._temp_dirs = set()

    def fetch(self, input_path: str) -> str:
        """
        Fetch a repo.
        If input_path is a URL, clone it to a temp dir.
        If input_path is a local path, validate it.
        Returns the absolute path to the repo.
        """
        if self._is_url(input_path):
            return self._clone_repo(input_path)
        else:
            if not os.path.exists(input_path):
                raise ValueError(f"Local path does not exist: {input_path}")
            return os.path.abspath(input_path)

    def _is_url(self, path: str) -> bool:
        """Check if path looks like a git URL."""
        # Simple regex for http/https/git/ssh
        regex = r'^(https?://|git@|ssh://|git://)'
        return re.match(regex, path) is not None

    def _clone_repo(self, url: str) -> str:
        """Clone repo to temp dir."""
        if not git:
            raise ImportError("GitPython is not installed. Cannot clone repositories.")

        temp_dir = tempfile.mkdtemp(prefix="omni_profiler_")
        try:
            git.Repo.clone_from(url, temp_dir)
            # Track this temp directory for cleanup
            self._temp_dirs.add(temp_dir)
            return temp_dir
        except Exception as e:
            # Cleanup if failed
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Failed to clone repository: {e}")

    def cleanup(self, path: str = None):
        """
        Cleanup temp dir if it was created by us.
        If path is provided, only cleanup that specific path if we created it.
        If path is None, cleanup all temp directories we created.
        """
        if path:
            # Only cleanup if this path is in our tracked set
            if path in self._temp_dirs and os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
                self._temp_dirs.discard(path)
        else:
            # Cleanup all tracked temp directories
            for temp_dir in list(self._temp_dirs):
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            self._temp_dirs.clear()
