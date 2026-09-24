"""Scaffold extraction and clustering, so the final list is not 40 near-identical analogs.
"""

from __future__ import annotations

from rdkit import Chem


def murcko_scaffold(mol: Chem.Mol) -> str:
    """Bemis-Murcko scaffold SMILES.

    INPUTS:   Molecule.
    OUTPUTS:  Scaffold SMILES ('' for an acyclic molecule).
    ACCEPTS:  tests/test_scaffolds.py -- LSD, lisuride and 2-bromo-LSD share an ergoline scaffold.
    EFFORT:   ~1 h.
    """

    raise NotImplementedError(
        "murcko_scaffold is not implemented; see the docstring for its contract."
    )


def butina_cluster(fps, cutoff: float = 0.65) -> list[int]:
    """Butina clustering on fingerprint similarity.

    INPUTS:   Fingerprint array, distance cutoff.
    OUTPUTS:  Cluster id per molecule.
    ACCEPTS:  tests/test_scaffolds.py -- identical molecules land in one cluster; cluster ids are
               deterministic.
    EFFORT:   ~3 h.
    """

    raise NotImplementedError(
        "butina_cluster is not implemented; see the docstring for its contract."
    )
