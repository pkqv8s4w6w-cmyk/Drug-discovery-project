"""ChEMBL bioactivity ingest.

Verified record counts as of 2026-09-24: 5-HT2A 7897 Ki / 2414 IC50 / 1456 EC50;
5-HT2B 3024 Ki / 1022 EC50; 5-HT2C 4671 Ki; 5-HT1A 6971 Ki.
"""

from __future__ import annotations

from pathlib import Path


def fetch_activities(target_chembl_id: str, standard_types: tuple[str, ...], cache_dir: Path):
    """Page through the ChEMBL activity endpoint with an on-disk cache.

    INPUTS:   Target id, endpoint types, cache directory.
    OUTPUTS:  DataFrame matching the raw schema in docs/data_provenance.md.
    ACCEPTS:  tests/test_chembl.py -- a cached fixture replays without network; pagination
               assembles the full record count.
    EFFORT:   ~1 day. Cache aggressively; these pulls are slow and the data is static between
              releases.
    """

    raise NotImplementedError(
        "fetch_activities is not implemented; see the docstring for its contract."
    )


def fetch_all_targets(config):
    """Fetch every target named in config.chembl.targets.

    INPUTS:   Resolved Config.
    OUTPUTS:  Path to data/processed/chembl_activities.parquet.
    ACCEPTS:  tests/test_chembl.py -- all four targets present; fetched_at and chembl_release
               recorded.
    EFFORT:   ~2 h.
    """

    raise NotImplementedError(
        "fetch_all_targets is not implemented; see the docstring for its contract."
    )
