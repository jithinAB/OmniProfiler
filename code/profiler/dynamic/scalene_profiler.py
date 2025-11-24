import subprocess
import json
import os
import sys
import tempfile
from typing import Dict, Any, Optional

class ScaleneProfiler:
    def __init__(self):
        pass

    def profile(self, script_path: str, args: list = None, work_dir: str = None, mock_inputs: list = None) -> Dict[str, Any]:
        """
        Run the script using Scalene and return the parsed JSON output.
        """
        if args is None:
            args = []
        
        # Prepare input string if mock_inputs provided
        input_str = None
        if mock_inputs:
            input_str = "\n".join(str(x) for x in mock_inputs) + "\n"

        # Create a temporary file for the JSON output
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
            json_output_path = tmp_file.name

        try:
            # Construct the command
            # python3 -m scalene --cli --no-browser --json --outfile <json_path> <script_path> <args>
            cmd = [
                sys.executable, "-m", "scalene",
                "--cli",
                "--no-browser",
                "--json",
                "--outfile", json_output_path,
                # Disable GPU by default on Mac to avoid crashes, enable if needed
                "--cpu", "--memory", 
                script_path
            ] + args

            # Run the command
            # We capture stdout/stderr to avoid cluttering the server logs
            # and to debug if needed.
            process = subprocess.run(
                cmd,
                cwd=work_dir or os.getcwd(),
                capture_output=True,
                text=True,
                input=input_str,
                timeout=10  # Add timeout to prevent hanging
            )

            if process.returncode != 0:
                # Scalene might return non-zero if the script fails
                # But we should still check if JSON was generated
                pass  # Don't print to avoid cluttering logs

            # Read the JSON output
            if os.path.exists(json_output_path) and os.path.getsize(json_output_path) > 0:
                with open(json_output_path, 'r') as f:
                    data = json.load(f)
                return data
            else:
                return {
                    "error": "Scalene failed to generate output",
                    "stderr": process.stderr[:500] if process.stderr else "",  # Limit error message length
                    "returncode": process.returncode
                }

        except subprocess.TimeoutExpired:
            return {"error": "Scalene profiling timed out"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            # Clean up - this runs AFTER the return statements
            if os.path.exists(json_output_path):
                try:
                    os.remove(json_output_path)
                except:
                    pass  # Ignore cleanup errors

    def _parse_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics from Scalene raw JSON for easier frontend consumption.
        """
        # This can be used to simplify the data structure if needed
        # For now, we return the full raw data and let frontend handle it
        return raw_data
