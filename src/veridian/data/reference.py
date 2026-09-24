"""Load and validate the reference set -- the ruler for everything downstream.

ADR-013: SMILES are resolved by identifier, never by name search. A ChEMBL name search
for '2-bromo-LSD' returns [3H]LSD, a different molecule with the opposite label.
"""

from __future__ import annotations

from pathlib import Path


def load_reference_set(path: Path | None = None):
    """Load reference_set.csv and validate every row.

    INPUTS:   Optional path override; defaults via veridian.paths.
    OUTPUTS:  DataFrame with the reference schema. Rows with smiles_source_type='not_resolved' are
               retained with null SMILES rather than dropped -- an honest gap, not a silent one.
    ACCEPTS:  tests/test_reference_set.py -- every non-null SMILES parses and its computed InChIKey
               matches the committed value; class_label is always hallucinogen or non_hallucinogen.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "load_reference_set is not implemented; see the docstring for its contract."
    )


def hard_pairs(df) -> dict[str, list[str]]:
    """Group reference compounds by hard_pair_group.

    INPUTS:   Reference DataFrame.
    OUTPUTS:  {group_name: [compound_id, ...]} for the discriminating pairs.
    ACCEPTS:  tests/test_reference_set.py -- ergoline_triad contains exactly REF001, REF007, REF008.
    EFFORT:   ~1 h. These pairs drive gate criteria G6 and G7.
    """

    raise NotImplementedError(
        "hard_pairs is not implemented; see the docstring for its contract."
    )
