"""Final selection: 20-50 compounds, clustered by scaffold.
"""

from __future__ import annotations


def select_candidates(df, config):
    """Diversity-aware final selection.

    INPUTS:   Scored candidate DataFrame, Config.
    OUTPUTS:  20-50 compounds clustered by scaffold, each carrying its full flag list. Ranking uses
               docking, differential and affinity/efficacy signals -- never the HTR classifier
               (ADR-008).
    ACCEPTS:  tests/test_select.py -- no scaffold cluster dominates the output; every selected
               compound carries a populated flags column; an out-of-domain HTR prediction does not
               change rank.
    EFFORT:   ~1 day.
    """

    raise NotImplementedError(
        "select_candidates is not implemented; see the docstring for its contract."
    )
