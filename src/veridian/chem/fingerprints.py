"""Molecular fingerprints. One featuriser, shared by every model, so that the
applicability-domain distance and the model inputs cannot silently diverge.
"""

from __future__ import annotations

import numpy as np
from rdkit import Chem


def ecfp4_counts(mols: list[Chem.Mol], n_bits: int = 2048) -> np.ndarray:
    """ECFP4 count fingerprints.

    INPUTS:   Molecules, bit width.
    OUTPUTS:  Integer array (n_mols, n_bits).
    ACCEPTS:  tests/test_fingerprints.py -- identical molecules give identical rows; output is
               deterministic.
    EFFORT:   ~2 h.
    """

    raise NotImplementedError(
        "ecfp4_counts is not implemented; see the docstring for its contract."
    )


def tanimoto_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pairwise MinMax-Tanimoto similarity between two count-fingerprint sets.

    INPUTS:   Two count arrays.
    OUTPUTS:  Similarity matrix in [0, 1].
    ACCEPTS:  tests/test_fingerprints.py -- self-similarity is exactly 1.0; matrix is symmetric.
    EFFORT:   ~2 h. Also backs the GP kernel in ml/kernels.py.
    """

    raise NotImplementedError(
        "tanimoto_matrix is not implemented; see the docstring for its contract."
    )
