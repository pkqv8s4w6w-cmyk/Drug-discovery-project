"""Cross-receptor score normalisation (ADR-006).

Raw Vina scores from 9AS9 (3.47 A) and 7WC9 (2.50 A) are not comparable: differences are
dominated by pocket volume, rotamer modelling and box definition rather than by biology.
Every receptor gets the same decoy background docked into it once, and all cross-structure
comparison uses robust z-scores.

Robust, not standard: docking score distributions are left-skewed, so median/MAD is
correct and mean/SD is not.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreNormalizer:
    receptor_id: str
    median: float
    mad: float



def fit_background(receptor_id: str, decoy_scores) -> ScoreNormalizer:
    """Fit a robust normaliser from the shared decoy background.

    INPUTS:   Receptor id, decoy score array.
    OUTPUTS:  ScoreNormalizer using median and 1.4826 * MAD.
    ACCEPTS:  tests/test_normalize.py -- outliers do not shift the fit the way mean/SD would.
    EFFORT:   ~3 h. The background run is ~19 h once, then cached permanently.
    """

    raise NotImplementedError(
        "fit_background is not implemented; see the docstring for its contract."
    )


def z(normalizer: ScoreNormalizer, scores):
    """Convert raw scores to robust z-scores.

    INPUTS:   Normaliser, score array.
    OUTPUTS:  z-score array.
    ACCEPTS:  tests/test_normalize.py -- z of the background median is 0.
    EFFORT:   ~1 h.
    """

    raise NotImplementedError(
        "z is not implemented; see the docstring for its contract."
    )
