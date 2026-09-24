"""Controls that make self-deception harder.

The potency-only baseline exists because HTR magnitude correlates strongly with 5-HT2A
potency and Emax, and most HTR-negatives are also weak or partial agonists. A naive
classifier learns potency, not hallucinogenicity, and looks excellent in cross-validation
while being scientifically empty.
"""

from __future__ import annotations


def potency_only_baseline(df):
    """Logistic regression on [pEC50_2A, emax_2A] alone.

    INPUTS:   Curated DataFrame with potency columns.
    OUTPUTS:  Fitted model plus cross-validated performance.
    ACCEPTS:  tests/test_baselines.py -- reported next to every structural model, always.
    EFFORT:   ~3 h.
    """

    raise NotImplementedError(
        "potency_only_baseline is not implemented; see the docstring for its contract."
    )


def one_nn_tanimoto(train_fps, train_y, query_fps):
    """1-nearest-neighbour Tanimoto control: 'is this just similarity search?'

    INPUTS:   Training fingerprints and labels, query fingerprints.
    OUTPUTS:  Predicted labels and the nearest-neighbour similarity.
    ACCEPTS:  tests/test_baselines.py -- a structural model that cannot beat 1-NN has not earned
               its complexity.
    EFFORT:   ~2 h.
    """

    raise NotImplementedError(
        "one_nn_tanimoto is not implemented; see the docstring for its contract."
    )
