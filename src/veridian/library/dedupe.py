"""InChIKey deduplication across routes and against known compounds.
"""

from __future__ import annotations


def dedupe(df, against: tuple[str, ...] = ('reference_set', 'chembl')):
    """Drop duplicates within the library and against known compound sets.

    INPUTS:   Library DataFrame, sets to deduplicate against.
    OUTPUTS:  Deduplicated DataFrame plus a dropped-rows report.
    ACCEPTS:  tests/test_dedupe.py -- a compound present in the reference set is removed and the
               removal is recorded, not silent.
    EFFORT:   ~4 h.
    """

    raise NotImplementedError(
        "dedupe is not implemented; see the docstring for its contract."
    )
