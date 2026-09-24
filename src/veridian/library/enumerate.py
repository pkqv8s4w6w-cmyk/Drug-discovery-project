"""Combinatorial enumeration, chunked and shardable.

Enumeration is cheap (~0.5-1.5 ms/product, so 1M is 15-40 min on 4 cores). Docking is not
(ADR-010). Never hold the full library in memory -- stream into parquet row groups.
"""

from __future__ import annotations

from pathlib import Path


def enumerate_library(config, shard: int = 0, n_shards: int = 1) -> Path:
    """Enumerate the configured routes, applying enumeration-time filters.

    INPUTS:   Config, shard index, shard count.
    OUTPUTS:  Path to a parquet shard: ligand_id, smiles_std, inchikey, route, bb_ids,
               n_synth_steps.
    ACCEPTS:  tests/test_enumerate.py -- sharding is a partition (no duplicates, nothing lost);
               every product passes chem.protonation.can_reach_d332; same seed gives identical
               output.
    EFFORT:   ~2 days. Filters run cheapest-first before any conformer is generated (ADR-011).
    """

    raise NotImplementedError(
        "enumerate_library is not implemented; see the docstring for its contract."
    )
