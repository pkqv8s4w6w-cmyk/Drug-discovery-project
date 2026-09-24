"""Docking box definition, derived deterministically from the native ligand.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Box:
    center: tuple[float, float, float]
    size: tuple[float, float, float]



def box_from_native(pdb_id: str, config) -> Box:
    """Build a docking box around the native ligand's extents.

    INPUTS:   PDB id, Config (supplies padding and edge clamps).
    OUTPUTS:  Box centred on the ligand centroid, padded and clamped.
    ACCEPTS:  tests/test_boxes.py -- the box contains every native ligand atom; same input gives
               byte-identical output.
    EFFORT:   ~3 h. Box geometry differs between structures, which is one reason raw scores are not
              comparable across receptors (ADR-006).
    """

    raise NotImplementedError(
        "box_from_native is not implemented; see the docstring for its contract."
    )
