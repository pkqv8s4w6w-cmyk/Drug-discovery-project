"""Bioactivity curation.

assay_mode and assay_readout are load-bearing, not decoration: the 2A functional records
mix agonist and antagonist assays, and Gq-versus-arrestin readout is central to the
partial-agonism proxy (ADR-007).
"""

from __future__ import annotations


def curate(raw_df):
    """Aggregate duplicates and parse assay metadata into the curated schema.

    INPUTS:   Raw ChEMBL DataFrame.
    OUTPUTS:  DataFrame with pchembl_median, pchembl_mad, n_records, assay_mode, assay_readout,
               emax_pct.
    ACCEPTS:  tests/test_curate.py -- duplicate measurements collapse to a median with a recorded
               MAD; censored relations ('>' '<') are flagged, not silently treated as exact.
    EFFORT:   ~2 days. The assay_description regex table is the bulk of it.
    """

    raise NotImplementedError(
        "curate is not implemented; see the docstring for its contract."
    )


def verified_inactives(curated_df, target: str, threshold: float = 5.0):
    """Extract measured inactives for the primary decoy set.

    INPUTS:   Curated DataFrame, target key, pChEMBL threshold.
    OUTPUTS:  DataFrame of compounds with measured pChEMBL below threshold.
    ACCEPTS:  tests/test_curate.py -- returns only rows with an actual measurement; never infers
               inactivity from absence of data.
    EFFORT:   ~3 h. These are real experimental negatives and carry no property-matching artifact.
    """

    raise NotImplementedError(
        "verified_inactives is not implemented; see the docstring for its contract."
    )
