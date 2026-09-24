"""Enrichment metrics with bootstrap confidence intervals.

Gate criteria G2 and G3 depend on these numbers, so the intervals matter as much as the
point estimates.
"""

from __future__ import annotations


def enrichment_factor(scores, labels, fraction: float = 0.01) -> float:
    """Enrichment factor at a given ranked fraction.

    INPUTS:   Score array, binary labels, fraction.
    OUTPUTS:  EF value.
    ACCEPTS:  tests/test_enrichment.py -- perfect ranking gives the theoretical maximum; random
               ranking gives ~1.0.
    EFFORT:   ~2 h.
    """

    raise NotImplementedError(
        "enrichment_factor is not implemented; see the docstring for its contract."
    )


def bootstrap_ci(metric_fn, scores, labels, n_boot: int = 1000, seed: int = 0):
    """Bootstrap confidence interval for any ranking metric.

    INPUTS:   Metric callable, scores, labels, resample count, seed.
    OUTPUTS:  (point estimate, lower bound, upper bound) at 95%.
    ACCEPTS:  tests/test_enrichment.py -- with n=6 vs 7 the interval is wide, roughly +/-0.20-0.25,
               which is the point: the reference set can kill the method but cannot confirm it
               (PREREGISTRATION 3).
    EFFORT:   ~3 h.
    """

    raise NotImplementedError(
        "bootstrap_ci is not implemented; see the docstring for its contract."
    )
