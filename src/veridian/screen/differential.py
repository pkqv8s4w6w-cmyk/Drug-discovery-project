"""Differential-pose scoring -- step 6, the project's central hypothesis (ADR-006).

Score each compound against the hallucinogenic-bound and non-hallucinogenic-bound
conformations separately, then rank by the difference.

This is a hypothesis, not an established method. Nobody has shown that pocket preference
predicts hallucinogenicity. It is implemented with two controls and a null so that a
negative result is reportable rather than quietly discarded:

  - partial_delta_z residualises on similarity to each family's native ligand, removing
    the induced-fit confound ('is this just more like IHCH-7086 than like LSD?').
  - A 1,000-fold permutation null shuffles the family assignment across the comparator
    structures. It re-uses cached scores and costs nothing.
  - delta_ifp supplements the score difference with interaction-fingerprint differences at
    the mechanistically implicated contacts, which is a far more defensible observable
    than score arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NullDist:
    observed: float
    permuted: tuple[float, ...]
    p_value: float



def differential_scores(df, families: dict[str, list[str]]):
    """Compute per-compound differential statistics across pocket families.

    INPUTS:   Docking results across all receptors (z-normalised), family assignment.
    OUTPUTS:  DataFrame: mean_z_nonhallu, mean_z_hallu, delta_z, delta_ifp, sim_to_native_max per
               family, partial_delta_z.
    ACCEPTS:  tests/test_differential.py -- operates on z-scores only; passing raw kcal/mol raises
               (ADR-006).
    EFFORT:   ~1.5 days.
    """

    raise NotImplementedError(
        "differential_scores is not implemented; see the docstring for its contract."
    )


def permutation_null(df, families, n_perm: int = 1000, seed: int = 0) -> NullDist:
    """Permutation null over family assignment.

    INPUTS:   Differential DataFrame, families, permutation count, seed.
    OUTPUTS:  NullDist with the observed separation, the permuted distribution and a p-value.
    ACCEPTS:  tests/test_differential.py -- under a synthetic no-signal dataset the p-value is
               uniform; a planted signal is recovered.
    EFFORT:   ~0.5 day. Gate criterion G5 depends on this.
    """

    raise NotImplementedError(
        "permutation_null is not implemented; see the docstring for its contract."
    )
