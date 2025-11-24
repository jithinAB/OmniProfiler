from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel, validator
from typing import Optional
import os
import shutil
import tempfile
import logging
from typing import Dict, Any
from code.profiler.orchestrator import Orchestrator
from code.profiler.repo_fetcher import RepoFetcher
from code.profiler.comparator import ProfilerComparator

logger = logging.getLogger(__name__)

app = FastAPI(title="Omni-Profiler API", version="1.0.0")

# Configuration constants
MAX_CODE_SIZE = 1024 * 1024  # 1MB
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Models
class CodeRequest(BaseModel):
    code: str
    function_name: Optional[str] = None
    warmup_runs: Optional[int] = 0

    @validator('code')
    def validate_code_size(cls, v):
        if len(v) > MAX_CODE_SIZE:
            raise ValueError(f"Code size exceeds maximum allowed size of {MAX_CODE_SIZE} bytes")
        if not v.strip():
            raise ValueError("Code cannot be empty")
        return v

class RepoRequest(BaseModel):
    url: str
    entry_point: Optional[str] = None

    @validator('url')
    def validate_url(cls, v):
        import re
        import os
        # Basic URL validation
        url_pattern = r'^(https?://|git@|ssh://|git://)'
        if re.match(url_pattern, v):
            return v
        
        # Check if it's a valid local path
        if os.path.exists(v):
            return v
            
        raise ValueError("Invalid repository URL format or local path does not exist")

class CompareRequest(BaseModel):
    report_a: Dict[str, Any]
    report_b: Dict[str, Any]

# Global Orchestrator
orchestrator = Orchestrator()
repo_fetcher = RepoFetcher()
comparator = ProfilerComparator()

@app.get("/")
def read_root():
    return {
        "status": "Omni-Profiler API is running",
        "version": "1.0.0",
        "warning": "This API executes arbitrary Python code. Use only with trusted code in secure environments."
    }

@app.post("/profile/code")
def profile_code(request: CodeRequest):
    """
    Profile a raw code snippet.

    WARNING: This endpoint executes arbitrary Python code.
    Use only with trusted code in secure, isolated environments.
    """
    tmp_path = None
    try:
        logger.info(f"Profiling code snippet of size {len(request.code)} bytes")

        # Create temp file for code
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as tmp:
            tmp.write(request.code)
            tmp_path = tmp.name

        # Profile the code
        report = orchestrator.profile_file(tmp_path, warmup_runs=request.warmup_runs)

        # Check for errors in the report
        if "error" in report and report["error"]:
            logger.error(f"Profiling error: {report['error']}")
            raise HTTPException(status_code=400, detail=f"Profiling failed: {report['error']}")

        return report

    except HTTPException:
        raise
    except ValueError as e:
        # Validation errors
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error profiling code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during profiling")
    finally:
        # Always cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {tmp_path}: {e}")

@app.post("/profile/file")
async def profile_file(file: UploadFile = File(...)):
    """
    Profile an uploaded Python file.

    WARNING: This endpoint executes uploaded Python code.
    Use only with trusted files in secure, isolated environments.
    """
    tmp_path = None
    try:
        logger.info(f"Profiling uploaded file: {file.filename}")

        # Validate file extension
        if not file.filename.endswith('.py'):
            raise HTTPException(status_code=400, detail="Only .py files are supported")

        # Read and validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File size exceeds maximum of {MAX_FILE_SIZE} bytes")

        if not content.strip():
            raise HTTPException(status_code=400, detail="File cannot be empty")

        # Write to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='wb') as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # Profile the file
        report = orchestrator.profile_file(tmp_path)

        # Check for errors
        if "error" in report and report["error"]:
            logger.error(f"Profiling error: {report['error']}")
            raise HTTPException(status_code=400, detail=f"Profiling failed: {report['error']}")

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error profiling file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during profiling")
    finally:
        # Always cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {tmp_path}: {e}")

@app.post("/profile/repo")
def profile_repo(request: RepoRequest):
    """
    Profile a repository.
    
    If entry_point is provided, performs dynamic profiling by executing the entry point.
    Otherwise, performs only static analysis.
    """
    repo_path = None
    try:
        logger.info(f"Fetching and analyzing repository: {request.url}")

        # Fetch/clone the repository
        repo_path = repo_fetcher.fetch(request.url)

        # Results container
        results = {
            "repo_path": repo_path,
            "files": [],
            "summary": {
                "total_files": 0,
                "analyzed_files": 0,
                "failed_files": 0
            }
        }

        # 1. Static Analysis (always run)
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    results["summary"]["total_files"] += 1
                    full_path = os.path.join(root, file)

                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            code = f.read()

                        complexity = orchestrator.static_analyzer.analyze_complexity(code)
                        halstead = orchestrator.static_analyzer.analyze_halstead(code)
                        big_o = orchestrator.static_analyzer.analyze_big_o(code)
                        raw_metrics = orchestrator.static_analyzer.analyze_raw_metrics(code)
                        maintainability = orchestrator.static_analyzer.analyze_maintainability(code)
                        call_graph = orchestrator.call_graph_builder.build(code)

                        results["files"].append({
                            "path": os.path.relpath(full_path, repo_path),
                            "complexity": complexity,
                            "halstead": halstead,
                            "big_o": big_o,
                            "raw_metrics": raw_metrics,
                            "maintainability": maintainability,
                            "call_graph": call_graph
                        })
                        results["summary"]["analyzed_files"] += 1

                    except Exception as e:
                        logger.warning(f"Failed to analyze {full_path}: {e}")
                        results["summary"]["failed_files"] += 1
                        continue

        # 2. Dynamic Profiling (if entry_point provided)
        if request.entry_point:
            entry_point_path = os.path.join(repo_path, request.entry_point)
            if not os.path.exists(entry_point_path):
                raise HTTPException(status_code=400, detail=f"Entry point '{request.entry_point}' not found in repository")
            
            logger.info(f"Running dynamic profiling on entry point: {request.entry_point}")
            
            # Run dynamic profiling in the repo context
            dynamic_report = orchestrator.profile_file(entry_point_path, cwd=repo_path)
            
            if "error" in dynamic_report and dynamic_report["error"]:
                logger.error(f"Dynamic profiling error: {dynamic_report['error']}")
                # We don't fail the whole request, just add the error to results
                results["dynamic_error"] = dynamic_report["error"]
            else:
                # Merge dynamic analysis results
                results["dynamic_analysis"] = dynamic_report.get("dynamic_analysis", {})
                results["scalene_analysis"] = dynamic_report.get("scalene_analysis", {})
                results["hardware"] = dynamic_report.get("hardware", {})
                
                # If the entry point was also statically analyzed, we might want to merge that info,
                # but for now keeping them separate is fine.

        logger.info(f"Repository analysis complete: {results['summary']}")
        return results

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error profiling repo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during repository profiling")
    finally:
        # Cleanup cloned repository
        if repo_path:
            try:
                repo_fetcher.cleanup(repo_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup repo directory {repo_path}: {e}")

# Simple in-memory history for now
history = []

@app.get("/history")
def get_history():
    """Get profiling history."""
    return history

# Middleware or decorator to save history would be better, 
# but for now let's just append in the endpoints manually or wrap them.
# To keep it simple for this phase, we'll just return an empty list or mock it.
# In a real app, we'd use a DB.

