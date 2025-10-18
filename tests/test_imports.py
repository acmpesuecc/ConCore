import importlib
import pytest

packages = [
    ("numpy", "numpy"),
    ("scipy", "scipy"),
    ("matplotlib", "matplotlib"),
    ("seaborn", "seaborn"),
    ("sklearn", "sklearn"),
    ("statsmodels", "statsmodels"),
    ("plotly", "plotly"),
    ("pandas", "pandas"),
]

@pytest.mark.parametrize("name,module", packages)
def test_import_package(name, module):
    """Smoke test: the package must import without raising."""
    importlib.import_module(module)