"""Surrogate-guided active learning (ADR-010).

This is how a million-compound library gets screened at all on this hardware. Brute-force
docking of 1M compounds is ~87 days on 4 cores; active learning over a ~1% docked fraction
is roughly two nights.

Recall loss is measured against a held-out fully-docked random sample, not cited from
someone else's benchmark.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ALResult:
    docked_ids: list[str]
    predicted_ranking: Path
    recall_at_top_500: float | None
    rounds: int



def active_learn(library_path: Path, engine, receptor, config) -> ALResult:
    """Run the surrogate-guided docking loop.

    INPUTS:   Library parquet, DockEngine, PreparedReceptor, Config (init_batch, n_rounds, batch,
              surrogate, acquisition, holdout_for_recall).
    OUTPUTS:  ALResult including measured recall against the held-out fully-docked sample.
    ACCEPTS:  tests/test_active_learning.py -- at smoke scale (2 rounds x 100) the loop completes
               and recall_at_top_500 is populated; a run without a holdout reports None rather than
               guessing a recall figure.
    EFFORT:   ~3 days. Real at smoke scale first, then scaled.
    """

    raise NotImplementedError(
        "active_learn is not implemented; see the docstring for its contract."
    )
