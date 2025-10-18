import importlib
import sys

packages = {
    "numpy": "numpy",
    "scipy": "scipy",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "sklearn": "sklearn",
    "statsmodels": "statsmodels",
    "plotly": "plotly",
    "pandas": "pandas",
}

failed = []
for name, modname in packages.items():
    try:
        m = importlib.import_module(modname)
        ver = getattr(m, "__version__", "unknown")
        print(f"OK: {name} imported, version: {ver}")
    except Exception as e:
        print(f"FAIL: {name} import failed: {e}", file=sys.stderr)
        failed.append(name)

if failed:
    raise SystemExit(f"Import failures: {failed}")