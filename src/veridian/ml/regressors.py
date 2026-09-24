"""Affinity and efficacy models: 2A pKi, 2A Emax (ADR-007), 2B agonism (ADR-002).
"""

from __future__ import annotations


def train_all(config):
    """Train every configured model with conformal intervals.

    INPUTS:   Resolved Config.
    OUTPUTS:  {model_name: fitted model}, plus metrics written to the run directory.
    ACCEPTS:  tests/test_regressors.py -- every model reports scaffold-split performance beside
               random-split performance.
    EFFORT:   ~2 days.
    """

    raise NotImplementedError(
        "train_all is not implemented; see the docstring for its contract."
    )


def predict_h2b_agonism(model, smiles: list[str]):
    """Predict 5-HT2B agonism and assign h2b_flag.

    INPUTS:   Fitted model, SMILES list.
    OUTPUTS:  DataFrame: pred_h2b_pec50, pred_h2b_emax, h2b_flag in {clear, watch, reject, abstain}.
    ACCEPTS:  tests/test_antitarget_filter.py::test_2b_filter_retains_reference_nonhallucinogens --
               lisuride and 2-bromo-LSD must NOT be rejected. They bind 2B tightly but are
               antagonists and are not valvulopathic; an affinity-based filter would delete two of
               this project's own reference negatives (ADR-002).
    EFFORT:   ~1 day.
    """

    raise NotImplementedError(
        "predict_h2b_agonism is not implemented; see the docstring for its contract."
    )
