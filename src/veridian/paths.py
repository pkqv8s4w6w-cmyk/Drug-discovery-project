"""Canonical path resolution.

Every path derives from a resolved `Config`. No module elsewhere joins a literal
directory name, so relocating the data tree is a config change rather than a grep.
"""

from __future__ import annotations

from pathlib import Path

from veridian.config import REPO_ROOT, Config


def _resolve(config: Config, key: str, default: str) -> Path:
    return REPO_ROOT / config.get(f"paths.{key}", default)


def reference_dir(config: Config) -> Path:
    return _resolve(config, "reference", "data/reference")


def reference_set_csv(config: Config) -> Path:
    return reference_dir(config) / "reference_set.csv"


def htr_corpus_csv(config: Config) -> Path:
    return reference_dir(config) / "htr_corpus.csv"


def raw_dir(config: Config) -> Path:
    return _resolve(config, "raw", "data/raw")


def interim_dir(config: Config) -> Path:
    return _resolve(config, "interim", "data/interim")


def processed_dir(config: Config) -> Path:
    return _resolve(config, "processed", "data/processed")


def results_dir(config: Config) -> Path:
    return _resolve(config, "results", "data/results")


def external_dir(config: Config) -> Path:
    return _resolve(config, "external", "data/external")


def structures_raw(config: Config) -> Path:
    return _resolve(config, "structures_raw", "structures/raw")


def structures_prepared(config: Config) -> Path:
    return _resolve(config, "structures_prepared", "structures/prepared")


def runs_dir(config: Config) -> Path:
    return _resolve(config, "runs", "runs")


def docking_results(config: Config, receptor_id: str) -> Path:
    """Parquet of docking results for one receptor at the current tier."""
    return results_dir(config) / "docking" / receptor_id / f"{config.tier}.parquet"


def ensure_dirs(config: Config) -> None:
    """Create every writable directory the pipeline needs."""
    for maker in (
        raw_dir, interim_dir, processed_dir, results_dir,
        external_dir, structures_raw, structures_prepared, runs_dir,
    ):
        maker(config).mkdir(parents=True, exist_ok=True)
