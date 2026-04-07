import importlib

import pytest

from app.services.feature_model.fm_analysis_facade import _run_flamapy_satisfiable


UVL_MINIMAL = """namespace TestModel

features
    Root
        optional Child
"""


def _flamapy_module_available() -> bool:
    module_candidates = [
        "flamapy.interfaces.python.flama_feature_model",
        "flamapy.interfaces.python.flamapy_feature_model",
    ]
    for module_name in module_candidates:
        try:
            importlib.import_module(module_name)
            return True
        except Exception:
            continue
    return False


def test_flamapy_integration_if_available():
    if not _flamapy_module_available():
        pytest.skip("Flamapy no está disponible en el entorno de test")

    result = _run_flamapy_satisfiable(UVL_MINIMAL)
    assert result is not None
    assert result is True


def test_flamapy_integration_returns_none_when_missing(monkeypatch):
    def _raise(*_args, **_kwargs):
        raise ModuleNotFoundError()

    monkeypatch.setattr(importlib, "import_module", _raise)
    assert _run_flamapy_satisfiable(UVL_MINIMAL) is None
