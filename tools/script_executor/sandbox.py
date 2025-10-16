import subprocess
import tempfile
import os
import sys

DEFAULT_TIMEOUT = 30
MAX_OUTPUT_CHARS = 50000

def run_script_safely(code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    with tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=".py", 
        mode="w", 
        encoding="utf-8"
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            cwd=os.getcwd()
        )
        
        stdout = (result.stdout or "")[:MAX_OUTPUT_CHARS]
        stderr = (result.stderr or "")[:MAX_OUTPUT_CHARS]
        
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
        try:
            os.remove(tmp_path)
        except Exception:
            pass