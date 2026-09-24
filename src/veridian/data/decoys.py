"""Decoy construction. Three sets, reported separately, never pooled (PREREGISTRATION 5.4).

Random decoys make docking look dramatically better than it is, because the model separates
on molecular weight and logP rather than on binding. Charge matching matters especially
here: every true active is a cation at pH 7.4, so unmatched decoys would make the
salt-bridge filter look like genius.
"""

from __future__ import annotations


def property_matched_decoys(actives_df, background_df, n_per_active: int = 50, seed: int = 0):
    """DUD-E/DEKOIS-style property-matched decoys.

    INPUTS:   Actives, background pool, decoys per active, seed.
    OUTPUTS:  DataFrame matched on MW, clogP, HBD, HBA, rotatable bonds and net formal charge at pH
               7.4, with ECFP4 Tanimoto < 0.35 to any active.
    ACCEPTS:  tests/test_decoys.py -- matched property distributions are statistically
               indistinguishable from the actives; no decoy exceeds the similarity ceiling.
    EFFORT:   ~1.5 days.
    """

    raise NotImplementedError(
        "property_matched_decoys is not implemented; see the docstring for its contract."
    )


def build_decoy_sets(config):
    """Build all three decoy sets.

    INPUTS:   Resolved Config.
    OUTPUTS:  {'verified_inactive': df, 'property_matched': df, 'random': df}.
    ACCEPTS:  tests/test_decoys.py -- the three sets are disjoint and separately labelled.
    EFFORT:   ~0.5 day. The random set exists only to quantify benchmark inflation.
    """

    raise NotImplementedError(
        "build_decoy_sets is not implemented; see the docstring for its contract."
    )
