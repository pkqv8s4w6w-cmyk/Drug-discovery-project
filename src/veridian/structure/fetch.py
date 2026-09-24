"""RCSB structure download with content hashing.
"""

from __future__ import annotations

from pathlib import Path


def fetch_structure(pdb_id: str, out_dir: Path, force: bool = False) -> Path:
    """Download one PDB entry and record its SHA-256.

    INPUTS:   PDB id, output directory, force re-download.
    OUTPUTS:  Path to the cached file; hash written to structures/MANIFEST.yaml.
    ACCEPTS:  tests/test_fetch.py -- a second call without force hits the cache and does not
               re-download.
    EFFORT:   ~3 h.
    """

    raise NotImplementedError(
        "fetch_structure is not implemented; see the docstring for its contract."
    )
