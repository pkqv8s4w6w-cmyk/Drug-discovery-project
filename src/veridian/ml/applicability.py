"""Applicability domain. AD coverage is a headline number, not a footnote.
"""

from __future__ import annotations


def ad_distance(query_fps, train_fps):
    """Distance to the training set: 1 - max Tanimoto similarity.

    INPUTS:   Query and training fingerprints.
    OUTPUTS:  Distance per query compound, plus k-NN distance at k=5.
    ACCEPTS:  tests/test_applicability.py -- a training compound has distance 0; a novel scaffold
               scores near 1.
    EFFORT:   ~3 h.
    """

    raise NotImplementedError(
        "ad_distance is not implemented; see the docstring for its contract."
    )


def coverage_fraction(distances, threshold: float) -> float:
    """Fraction of compounds inside the applicability domain.

    INPUTS:   Distance array, threshold (95th percentile of calibration distances).
    OUTPUTS:  Fraction in [0, 1]. Expected to be near zero for a bespoke library -- report it
               plainly rather than burying it (ADR-008).
    ACCEPTS:  tests/test_applicability.py -- returns 1.0 for the training set itself.
    EFFORT:   ~1 h.
    """

    raise NotImplementedError(
        "coverage_fraction is not implemented; see the docstring for its contract."
    )
