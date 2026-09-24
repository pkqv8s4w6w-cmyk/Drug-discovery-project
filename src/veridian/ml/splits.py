"""Train/test splits, in increasing order of honesty.

Random CV, then Murcko-scaffold, then leave-one-chemotype-out. All three are reported.
The gap between random CV and LOCO is the real result, and it will be large.
"""

from __future__ import annotations


def scaffold_split(df, n_folds: int = 5, seed: int = 0):
    """Murcko-scaffold-grouped k-fold split.

    INPUTS:   DataFrame with a murcko_scaffold column, fold count, seed.
    OUTPUTS:  Fold assignment per row; no scaffold spans two folds.
    ACCEPTS:  tests/test_splits.py -- scaffold groups never straddle folds.
    EFFORT:   ~3 h.
    """

    raise NotImplementedError(
        "scaffold_split is not implemented; see the docstring for its contract."
    )


def leave_one_chemotype_out(df):
    """Leave-one-chemotype-out split across the chemotype classes.

    Classes: phenethylamine, tryptamine, ergoline, isoDMT, azepinoindole,
    constrained-other.

    INPUTS:   DataFrame with a chemotype column.
    OUTPUTS:  Iterator of (train_idx, test_idx) per held-out chemotype.
    ACCEPTS:  tests/test_splits.py -- every chemotype is held out exactly once.
    EFFORT:   ~3 h. This is the split that tells you whether the model generalises off its training
              chemotypes -- which is the entire question for a bespoke library.
    """

    raise NotImplementedError(
        "leave_one_chemotype_out is not implemented; see the docstring for its contract."
    )
