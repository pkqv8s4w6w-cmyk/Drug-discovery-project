"""Parallel docking dispatch with resume.

Four single-threaded Vina processes, never one four-threaded process: Vina is
non-deterministic with --cpu > 1 even at a fixed seed (ADR-012). Single-threading is also
faster here, so determinism costs nothing.

At scale the runner must stream. 1M ligands x 9 poses is 25-40 GB against 30 GB free, so
poses are parsed, scored, reduced to the top 3 gzipped, and the rest discarded.
"""

from __future__ import annotations

from pathlib import Path


def dock_library(library_path: Path, receptor, config) -> Path:
    """Dock a library shard against one receptor.

    INPUTS:   Library parquet, PreparedReceptor, Config.
    OUTPUTS:  Path to a docking-results parquet (schema in docs/data_provenance.md).
    ACCEPTS:  tests/test_dock_runner.py -- 20 ligands reproduce byte-identical parquet across two
               runs at a fixed seed; resume after SIGKILL loses no completed work and repeats none.
    EFFORT:   ~2 days.
    """

    raise NotImplementedError(
        "dock_library is not implemented; see the docstring for its contract."
    )


def emit_jobspec(config, out_path: Path) -> Path:
    """Write a shardable job spec for external execution.

    INPUTS:   Config (compute.dispatch selects the format), output path.
    OUTPUTS:  Path to a SLURM array or AWS Batch job spec. Emits only; never submits.
    ACCEPTS:  tests/test_dock_runner.py -- shard count x shard size equals the dock budget.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "emit_jobspec is not implemented; see the docstring for its contract."
    )
