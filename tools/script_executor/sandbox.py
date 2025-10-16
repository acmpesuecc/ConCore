import subprocess
import tempfile
import os
import sys

# Safety configurations
DEFAULT_TIMEOUT = 30  # Increased for data processing
MAX_OUTPUT_CHARS = 50000  # Increased for larger outputs

def run_script_safely(code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Execute Python code in a subprocess sandbox.
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        dict with 'stdout' and 'stderr' keys
    """
    # Create temporary file with the code
    with tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=".py", 
        mode="w", 
        encoding="utf-8"
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        # Execute in subprocess with timeout
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            cwd=os.getcwd()  # Use current working directory
        )
        
        stdout = (result.stdout or "")[:MAX_OUTPUT_CHARS]
        stderr = (result.stderr or "")[:MAX_OUTPUT_CHARS]
        
        # Truncation warning
        if len(result.stdout or "") > MAX_OUTPUT_CHARS:
            stdout += f"\n... [Output truncated at {MAX_OUTPUT_CHARS} characters]"
        if len(result.stderr or "") > MAX_OUTPUT_CHARS:
            stderr += f"\n... [Error output truncated at {MAX_OUTPUT_CHARS} characters]"
        
        return {
            "stdout": stdout,
            "stderr": stderr,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds",
            "returncode": -1
        }
        
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "returncode": -1
        }
        
    finally:
        # Clean up temporary file
        try:
            os.remove(tmp_path)
        except Exception:
            pass