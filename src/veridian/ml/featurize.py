"""Feature matrices, cached. One featuriser shared by every model.
"""

from __future__ import annotations


def featurize(smiles: list[str], config):
    """Build the model input matrix from SMILES.

    INPUTS:   SMILES list, Config (selects fingerprint and descriptor block).
    OUTPUTS:  (X array, feature-name list). Cached by content hash.
    ACCEPTS:  tests/test_featurize.py -- identical input gives identical output; the cache hit
               produces the same array as a cold computation.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "featurize is not implemented; see the docstring for its contract."
    )
