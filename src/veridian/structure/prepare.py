"""Receptor preparation. The stage that quietly eats days.

6WHA is a cryo-EM 5-HT2A-miniGq-Gbeta-gamma-scFv16 complex; 4IB4 is an X-ray structure
with a BRIL fusion and thermostabilising mutations. Everything except the receptor chain
must go, and every mutation must be recorded rather than silently accepted -- a
thermostabilising mutation inside the pocket invalidates that structure for this project.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreparedReceptor:
    pdb_id: str
    pdbqt_path: Path
    clean_pdb_path: Path
    chain: str
    mutations: tuple[str, ...]



def prepare_receptor(pdb_id: str, config) -> PreparedReceptor:
    """Strip non-receptor components, protonate at pH 7.4, write PDBQT.

    INPUTS:   PDB id, resolved Config.
    OUTPUTS:  PreparedReceptor; mutations recorded to structures/MANIFEST.yaml.
    ACCEPTS:  tests/test_prepare.py -- G-protein and scFv chains are absent from the output;
               assert_key_residues passes against the cleaned structure.
    EFFORT:   ~3 days. The single most error-prone stage in the pipeline.
    """

    raise NotImplementedError(
        "prepare_receptor is not implemented; see the docstring for its contract."
    )


def native_ligand(pdb_id: str, config):
    """Extract the co-crystallised ligand with correct bond orders.

    INPUTS:   PDB id, Config.
    OUTPUTS:  RDKit molecule with bond orders from the PDB chemical component dictionary.
    ACCEPTS:  tests/test_prepare.py -- the 6WHA ligand matches REF006's InChIKey.
    EFFORT:   ~1 day. Use the CCD, never bond-order perception from coordinates alone.
    """

    raise NotImplementedError(
        "native_ligand is not implemented; see the docstring for its contract."
    )
