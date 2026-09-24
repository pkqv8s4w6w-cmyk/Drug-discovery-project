"""The HTR classifier.

ADR-008: this model REPORTS. It never filters and never ranks.

Its training corpus is ~80-140 compounds, roughly 85% phenethylamine or tryptamine, with
only ~12-25 true negatives. The library this project builds is almost entirely outside its
applicability domain, so an out-of-domain abstention is the expected output, not a
failure. The 'HTR in-domain' table in the report is permitted to be empty.

Primary estimator is a GP with a Tanimoto kernel -- its native predictive variance gives a
principled AD signal for free, it is strong below N=500, and it has almost no
hyperparameters to overfit. A neural network at N=150 would produce confidently wrong
probabilities, which is precisely the failure this project cannot tolerate.
"""

from __future__ import annotations


def train_htr(config):
    """Train the HTR classifier with Mondrian conformal calibration.

    INPUTS:   Resolved Config.
    OUTPUTS:  Fitted MondrianConformalClassifier plus a CoverageReport.
    ACCEPTS:  tests/test_htr_classifier.py -- the potency-only baseline is always reported
               alongside; if the structural model does not beat it by more than its own CV spread,
               the report states that no hallucinogenicity signal was demonstrated (PREREGISTRATION
               5.3).
    EFFORT:   ~2 days. Blocked on the hand-extracted corpus.
    """

    raise NotImplementedError(
        "train_htr is not implemented; see the docstring for its contract."
    )


def predict_htr(model, smiles: list[str], config):
    """Predict with conformal sets and applicability-domain flags.

    INPUTS:   Fitted model, SMILES list, Config.
    OUTPUTS:  DataFrame: htr_pred_label, htr_pred_proba, htr_conformal_set, htr_in_domain,
               htr_ad_distance. Never returns a bare label without its domain flag.
    ACCEPTS:  tests/test_htr_classifier.py -- a tetrahydro-beta-carboline is flagged out of domain.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "predict_htr is not implemented; see the docstring for its contract."
    )
