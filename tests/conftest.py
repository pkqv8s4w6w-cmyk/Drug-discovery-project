"""Shared fixtures."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def reference_rows() -> list[dict[str, str]]:
    """The reference set, read with the stdlib so the fixture works without pandas."""
    path = REPO_ROOT / "data" / "reference" / "reference_set.csv"
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.fixture(scope="session")
def receptors() -> dict:
    from veridian.config import load_receptors

    return load_receptors()
