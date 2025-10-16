import subprocess
import tempfile
import os
import sys

# Keep timeout and output truncation to avoid runaway
DEFAULT_TIMEOUT = 10
MAX_OUTPUT_CHARS = 20000

def run_script_safely(code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Write the provided code to a temp file and run it in a subprocess using the current
    Python interpreter. Returns dict with stdout and stderr (both strings).
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        stdout = (result.stdout or "")[:MAX_OUTPUT_CHARS]
        stderr = (result.stderr or "")[:MAX_OUTPUT_CHARS]
        return {"stdout": stdout, "stderr": stderr}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out"}
    except Exception as e:
        return {"stdout": "", "stderr": f"Execution error: {str(e)}"}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
