"""Every stub must be honest about being a stub.

The contract convention: a stub raises NotImplementedError and its docstring carries
INPUTS, OUTPUTS, ACCEPTS and EFFORT. That way there is never ambiguity about whether a
module is finished, and filling one in is mechanical rather than archaeological.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import pytest

import veridian

REQUIRED_FIELDS = ("INPUTS:", "OUTPUTS:", "ACCEPTS:", "EFFORT:")

# Modules that are fully implemented and therefore exempt.
IMPLEMENTED = {
    "veridian.config",
    "veridian.paths",
    "veridian.provenance",
    "veridian.cli",
    "veridian.structure.residues",
    "veridian.ml.conformal",
}


def _modules():
    for info in pkgutil.walk_packages(veridian.__path__, prefix="veridian."):
        yield info.name


def _stub_callables(module):
    """Callables defined in this module that raise NotImplementedError."""
    for name, obj in vars(module).items():
        if name.startswith("_") or getattr(obj, "__module__", None) != module.__name__:
            continue
        if not (inspect.isfunction(obj) or inspect.isclass(obj)):
            continue
        source = inspect.getsource(obj)
        if "NotImplementedError" in source:
            yield name, obj


@pytest.mark.parametrize("module_name", sorted(_modules()))
def test_module_imports(module_name):
    """Import is the minimum bar: a skeleton with import errors is not walkable."""
    pytest.importorskip("rdkit")
    importlib.import_module(module_name)


def test_every_stub_declares_its_contract():
    pytest.importorskip("rdkit")
    violations = []
    for module_name in _modules():
        module = importlib.import_module(module_name)
        for name, obj in _stub_callables(module):
            doc = inspect.getdoc(obj) or ""
            missing = [f for f in REQUIRED_FIELDS if f not in doc]
            if missing:
                violations.append(f"{module_name}.{name} missing {', '.join(missing)}")
    assert not violations, "stubs without a full contract:\n  " + "\n  ".join(violations)


def test_stubs_raise_with_a_pointer_to_their_contract():
    pytest.importorskip("rdkit")
    from veridian.library.enumerate import enumerate_library

    with pytest.raises(NotImplementedError, match="contract"):
        enumerate_library(None)
