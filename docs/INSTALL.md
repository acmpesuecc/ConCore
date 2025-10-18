# Installing Data-Science Dependencies (local dev)

Recommended workflow:

1. Create and activate a virtual environment:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1   # PowerShell on Windows
   # or
   .\.venv\Scripts\activate.bat   # cmd
   # or (mac/linux)
   source .venv/bin/activate

2. Upgrade pip and install pinned requirements:
   python -m pip install --upgrade pip
   pip install -r requirements.txt

3. Run the smoke test to confirm imports:
   python -m pytest -q tests/test_imports.py

Notes:
- Requirements are pinned to specific versions to reduce surface for unexpected transitive changes.
- If installation fails on a given Python version, try using Python 3.10–3.12 (CI tests these).
- For production or containerized deployments, prefer creating a locked artifact (e.g., pip-compile or pip freeze + hash-checking).
- Running arbitrary user-generated code has security risks; run in an isolated environment and consider containerization for production.