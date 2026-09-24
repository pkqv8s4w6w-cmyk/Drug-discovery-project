"""RDKit descriptors, CNS MPO and synthetic accessibility.
"""

from __future__ import annotations

from rdkit import Chem


def cns_mpo(mol: Chem.Mol) -> float:
    """CNS multiparameter optimisation score (0-6).

    INPUTS:   RDKit molecule.
    OUTPUTS:  Float 0-6 summing the six desirability functions (clogP, clogD, MW, TPSA, HBD, pKa).
    ACCEPTS:  tests/test_descriptors.py -- a known CNS drug scores >= 4; a large polar molecule
               scores < 3.
    EFFORT:   ~1 day. Needs estimate_basic_pka from chem.protonation for the pKa term.
    """

    raise NotImplementedError(
        "cns_mpo is not implemented; see the docstring for its contract."
    )


def sa_score(mol: Chem.Mol) -> float:
    """Ertl synthetic accessibility (1 easy - 10 hard).

    INPUTS:   RDKit molecule.
    OUTPUTS:  Float 1-10.
    ACCEPTS:  tests/test_descriptors.py -- aspirin < 3, a complex natural product > 5.
    EFFORT:   ~2 h. Sanity check only, not a filter (ADR-011).
    """

    raise NotImplementedError(
        "sa_score is not implemented; see the docstring for its contract."
    )


def descriptor_frame(smiles: list[str]):
    """Compute the full descriptor block for a list of SMILES.

    INPUTS:   SMILES list.
    OUTPUTS:  DataFrame: mw, clogp, tpsa, hbd, hba, rotb, qed, cns_mpo, sa_score, murcko_scaffold.
    ACCEPTS:  tests/test_descriptors.py -- column set matches configs/filters.yaml keys exactly.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "descriptor_frame is not implemented; see the docstring for its contract."
    )
