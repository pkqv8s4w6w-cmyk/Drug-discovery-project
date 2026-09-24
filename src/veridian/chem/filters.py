"""Structural alert filters, applied at enumeration time (ADR-011).
"""

from __future__ import annotations

from rdkit import Chem


def passes_alerts(
    mol: Chem.Mol,
    catalogs: tuple[str, ...] = ("PAINS", "BRENK", "NIH"),
) -> tuple[bool, list[str]]:
    """Screen a molecule against RDKit FilterCatalog.

    INPUTS:   Molecule, catalog names.
    OUTPUTS:  (passed, list of triggered alert names).
    ACCEPTS:  tests/test_filters.py -- a known PAINS compound (catechol) is flagged; serotonin is
               not.
    EFFORT:   ~3 h.
    """

    raise NotImplementedError(
        "passes_alerts is not implemented; see the docstring for its contract."
    )


def passes_properties(mol: Chem.Mol, window: dict) -> tuple[bool, list[str]]:
    """Apply the CNS property window from configs/filters.yaml.

    INPUTS:   Molecule, property window dict.
    OUTPUTS:  (passed, list of violated property names).
    ACCEPTS:  tests/test_filters.py -- every reference compound passes; a >600 Da molecule fails on
               mw.
    EFFORT:   ~2 h.
    """

    raise NotImplementedError(
        "passes_properties is not implemented; see the docstring for its contract."
    )
