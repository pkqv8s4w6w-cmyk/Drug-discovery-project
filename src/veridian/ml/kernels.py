"""MinMax-Tanimoto kernel for scikit-learn Gaussian Processes.

Hand-rolled over a precomputed Gram matrix (~40 lines) rather than pulling in gauche,
which drags GPyTorch and torch -- a ~2 GB install with no benefit on a GPU-less box.
"""

from __future__ import annotations


class TanimotoKernel:
    """sklearn Kernel subclass computing MinMax-Tanimoto over count fingerprints.

    INPUTS:   Two count-fingerprint arrays.
    OUTPUTS:  Gram matrix, and its gradient when required by the GP fit.
    ACCEPTS:  tests/test_kernels.py -- the matrix is symmetric positive semi-definite and its
               diagonal is 1.0.
    EFFORT:   ~0.5 day.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError(
            "TanimotoKernel is not implemented; see the class docstring for its contract."
        )
