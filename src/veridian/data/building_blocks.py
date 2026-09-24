"""Enamine building-block ingest.

BLOCKED: the Enamine catalogue is behind registration and cannot be fetched
automatically. A ~500-block sample ships in data/external/ for development; the loader
contract below is what a full catalogue must satisfy.
"""

from __future__ import annotations

from pathlib import Path


def load_building_blocks(path: Path, role: str):
    """Load building blocks and filter to those matching a reaction role.

    INPUTS:   Catalogue path, role name from a configs/reactions/*.yaml entry.
    OUTPUTS:  DataFrame: bb_id, smiles, role, mw, price_tier, availability.
    ACCEPTS:  tests/test_building_blocks.py -- the shipped sample loads; role SMARTS filtering
               returns only matching blocks.
    EFFORT:   ~0.5 day once a catalogue is in hand. BLOCKED on registration-gated download.
    """

    raise NotImplementedError(
        "load_building_blocks is not implemented; see the docstring for its contract."
    )
