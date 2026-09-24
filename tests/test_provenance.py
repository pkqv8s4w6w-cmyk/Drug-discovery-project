"""Provenance, and the pre-registration drift check.

A pre-registration that can be quietly edited afterwards is not a pre-registration.
"""

from __future__ import annotations

from veridian.config import load_config
from veridian.provenance import (
    RunManifest,
    check_preregistration_drift,
    compute_run_id,
    preregistration_hash,
    sha256_file,
)


def test_preregistration_exists_and_hashes(repo_root):
    assert (repo_root / "PREREGISTRATION.md").is_file()
    assert preregistration_hash() is not None


def test_run_id_is_deterministic():
    config = load_config("smoke")
    assert compute_run_id(config) == compute_run_id(config)


def test_different_tiers_give_different_run_ids():
    assert compute_run_id(load_config("smoke")) != compute_run_id(load_config("dev"))


def test_manifest_records_the_preregistration_hash():
    manifest = RunManifest.start(load_config("smoke"))
    assert manifest.preregistration_sha256 == preregistration_hash()


def test_no_drift_reported_when_hashes_agree():
    assert check_preregistration_drift(preregistration_hash()) is None


def test_drift_is_reported_when_the_hash_changed():
    warning = check_preregistration_drift("0" * 64)
    assert warning is not None
    assert "changed" in warning


def test_stage_timing_is_recorded():
    manifest = RunManifest.start(load_config("smoke"))
    with manifest.stage("demo"):
        pass
    assert manifest.stages[0]["name"] == "demo"
    assert manifest.stages[0]["failed"] is False


def test_stage_records_failure():
    manifest = RunManifest.start(load_config("smoke"))
    try:
        with manifest.stage("boom"):
            raise RuntimeError("expected")
    except RuntimeError:
        pass
    assert manifest.stages[0]["failed"] is True


def test_sha256_file_matches_across_calls(repo_root):
    path = repo_root / "PREREGISTRATION.md"
    assert sha256_file(path) == sha256_file(path)
