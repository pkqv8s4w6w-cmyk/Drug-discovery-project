"""Structure validation. Catches the silent failures.
"""

from __future__ import annotations


def validate_structure(pdb_id: str, config) -> list[str]:
    """Check a prepared structure against its panel entry.

    INPUTS:   PDB id, Config.
    OUTPUTS:  List of problems (empty when clean): residue-map mismatches, missing key residues,
               SEQRES differences against UniProt, pocket mutations.
    ACCEPTS:  tests/test_residue_mapping.py -- D3.32 resolves to D155 in 6WHA and D135 in 4IB4; a
               deliberately corrupted map is rejected.
    EFFORT:   ~1.5 days. Flips the `verify: true` flags in configs/receptors.yaml once confirmed.
    """

    raise NotImplementedError(
        "validate_structure is not implemented; see the docstring for its contract."
    )
