"""Configuration resolution and the invariants that guard hardware realities."""

from __future__ import annotations

import pytest

from veridian.config import VALID_TIERS, ConfigError, load_config, load_receptors


@pytest.mark.parametrize("tier", VALID_TIERS)
def test_every_tier_resolves(tier):
    config = load_config(tier)
    assert config.tier == tier
    assert config.get("seed") is not None


def test_unknown_tier_raises():
    with pytest.raises(ConfigError, match="unknown tier"):
        load_config("nonsense")


def test_tier_overrides_base():
    assert load_config("dev").get("library.n_target") == 2000


def test_config_hash_is_stable():
    assert load_config("smoke").sha256() == load_config("smoke").sha256()


def test_tiers_have_distinct_hashes():
    assert load_config("smoke").sha256() != load_config("dev").sha256()


def test_vina_multithreading_is_rejected():
    """ADR-012: Vina is non-deterministic with --cpu > 1 even at a fixed seed."""
    with pytest.raises(ConfigError, match="non-deterministic"):
        load_config("dev", overrides={"compute": {"vina_cpu_per_process": 4}})


def test_dock_budget_cannot_exceed_library_size():
    """ADR-010: the dock budget is a subset of the enumerated library."""
    with pytest.raises(ConfigError, match="exceeds"):
        load_config("dev", overrides={"screen": {"n_dock_budget": 999_999}})


def test_full_tier_dock_budget_is_far_below_library_size():
    """1M brute-force docking is ~87 days on 4 cores; the gap is bridged by active learning."""
    config = load_config("full")
    assert config.get("screen.n_dock_budget") < config.get("library.n_target") / 10
    assert config.get("screen.active_learning.enabled") is True


def test_receptor_panel_families_are_disjoint():
    panel = load_receptors()
    seen: set[str] = set()
    for members in panel["families"].values():
        for pdb_id in members:
            assert pdb_id not in seen, f"{pdb_id} appears in two families"
            seen.add(pdb_id)


def test_every_family_member_is_defined():
    panel = load_receptors()
    for family, members in panel["families"].items():
        for pdb_id in members:
            assert pdb_id in panel["receptors"], f"{pdb_id} in {family} has no entry"


def test_differential_families_are_balanced():
    """Delta-z compares two families; a lopsided panel would bias the difference."""
    panel = load_receptors()
    hallu = panel["families"]["hallucinogenic"]
    non_hallu = panel["families"]["non_hallucinogenic"]
    assert len(hallu) == len(non_hallu) == 4


def test_redock_thresholds_are_resolution_aware():
    """PREREGISTRATION G1: a flat 2 A threshold would chase phantom bugs at 3.4 A."""
    panel = load_receptors()
    for pdb_id, entry in panel["receptors"].items():
        resolution = entry.get("resolution")
        threshold = entry.get("redock_threshold_angstrom")
        if resolution is None or threshold is None:
            continue
        if resolution >= 3.2:
            assert threshold >= 2.5, f"{pdb_id} at {resolution} A has a too-strict threshold"
        elif resolution <= 2.8:
            assert threshold <= 2.5, f"{pdb_id} at {resolution} A has a too-loose threshold"
