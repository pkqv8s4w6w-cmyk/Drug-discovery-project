"""ADR-003: D3.32 is D155 in 5-HT2A and D135 in 5-HT2B.

Hardcoding 155 does not crash against a 5-HT2B structure. It silently selects the wrong
residue, and every salt-bridge distance, pose filter and interaction fingerprint computed
against the antitarget panel becomes meaningless while looking entirely normal. That is
the failure this test exists to prevent.
"""

from __future__ import annotations

import pytest

from veridian.structure.residues import (
    ResidueMappingError,
    assert_key_residues,
    key_residues,
    orthosteric_aspartate,
    resolve,
)


def test_d332_is_d155_in_5ht2a():
    ref = orthosteric_aspartate("6WHA")
    assert ref.one_letter == "D"
    assert ref.seq_id == 155


def test_d332_is_d135_in_5ht2b():
    """The whole point of ADR-003."""
    ref = orthosteric_aspartate("4IB4")
    assert ref.one_letter == "D"
    assert ref.seq_id == 135


def test_2a_and_2b_aspartates_differ():
    assert orthosteric_aspartate("6WHA").seq_id != orthosteric_aspartate("4IB4").seq_id


@pytest.mark.parametrize("pdb_id", ["6WHA", "7WC9", "8UWL", "9ARZ", "9AS3", "9AS7", "7WC4"])
def test_every_5ht2a_structure_maps_to_155(pdb_id):
    assert orthosteric_aspartate(pdb_id).seq_id == 155


@pytest.mark.parametrize("pdb_id", ["6DRX", "6DRY", "6DRZ", "6DS0", "4IB4"])
def test_every_5ht2b_structure_maps_to_135(pdb_id):
    assert orthosteric_aspartate(pdb_id).seq_id == 135


def test_unknown_structure_raises():
    with pytest.raises(ResidueMappingError, match="not in the receptor panel"):
        resolve("XXXX", "3.32")


def test_unmapped_bw_number_raises():
    with pytest.raises(ResidueMappingError, match="not mapped"):
        resolve("6WHA", "9.99")


def test_key_residues_cover_the_mechanistic_contacts():
    """The contacts the differential hypothesis is actually about."""
    residues = key_residues("6WHA")
    for bw in ("3.32", "5.39", "6.48", "6.51", "6.52"):
        assert bw in residues


def test_assert_key_residues_accepts_a_matching_structure():
    observed = {ref.seq_id: _three(ref.one_letter) for ref in key_residues("6WHA").values()}
    assert_key_residues("6WHA", observed)


def test_assert_key_residues_rejects_a_mismatched_structure():
    """A corrupted map must fail loudly rather than produce quiet nonsense."""
    observed = {ref.seq_id: _three(ref.one_letter) for ref in key_residues("6WHA").values()}
    observed[155] = "ALA"          # D155 -> A155
    with pytest.raises(ResidueMappingError, match="does not match"):
        assert_key_residues("6WHA", observed)


def _three(one: str) -> str:
    from veridian.structure.residues import THREE_TO_ONE

    return next(k for k, v in THREE_TO_ONE.items() if v == one)
