"""3-D conformer generation and PDBQT preparation.

At full scale this is a real cost, not a formality: ~0.4 s/mol means 1M compounds is ~28 h
on 4 cores before a single docking job starts.
"""

from __future__ import annotations

from pathlib import Path

from rdkit import Chem


def embed_and_minimise(mol: Chem.Mol, seed: int = 0) -> Chem.Mol:
    """ETKDGv3 embedding followed by MMFF94s minimisation.

    INPUTS:   Molecule, RNG seed (required -- embedding is stochastic).
    OUTPUTS:  Molecule with one 3-D conformer.
    ACCEPTS:  tests/test_conformers.py -- same seed gives identical coordinates.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "embed_and_minimise is not implemented; see the docstring for its contract."
    )


def to_pdbqt(mol: Chem.Mol, out_path: Path) -> Path:
    """Write a docking-ready PDBQT via meeko.

    INPUTS:   Embedded molecule, output path.
    OUTPUTS:  Path to the written PDBQT.
    ACCEPTS:  tests/test_conformers.py -- the file parses and its torsion count matches RDKit's.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "to_pdbqt is not implemented; see the docstring for its contract."
    )
