"""Reference-set separation -- gate criteria G4, G6 and G7.

G6 and G7 are the criteria that matter. LSD, lisuride and 2-bromo-LSD are near-identical
ergolines with opposite behavioural labels; LSD and lisuride differ by a single
amide-to-urea substitution. Any method that separates the reference set while failing the
hard pairs is separating on gross chemotype and has learned nothing useful.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HardPairVerdict:
    group: str
    passed: bool
    detail: str



def separation_auc(df, reference_df):
    """AUC separating hallucinogens from non-hallucinogens on delta_z.

    INPUTS:   Differential scores, reference set.
    OUTPUTS:  (AUC, 95% bootstrap CI).
    ACCEPTS:  tests/test_separation.py -- the reported CI is wide at n=6 vs 7 and is never omitted.
    EFFORT:   ~3 h.
    """

    raise NotImplementedError(
        "separation_auc is not implemented; see the docstring for its contract."
    )


def check_hard_pairs(df, reference_df) -> list[HardPairVerdict]:
    """Evaluate gate criteria G6 and G7.

    INPUTS:   Differential scores, reference set.
    OUTPUTS:  One verdict per hard pair: lisuride and 2-bromo-LSD must each rank as less
               hallucinogen-like than LSD.
    ACCEPTS:  tests/test_hard_pairs.py -- marked xfail. It fails today, and it stays visible in
               every test run as a standing reminder of the project's central difficulty.
    EFFORT:   ~4 h.
    """

    raise NotImplementedError(
        "check_hard_pairs is not implemented; see the docstring for its contract."
    )
