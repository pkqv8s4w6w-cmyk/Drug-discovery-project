"""The D155 salt-bridge gate.

Every enumerated molecule must retain a basic nitrogen capable of the conserved D3.32 salt
bridge. The naive implementations of this check all leak: a bare [N] match, NumHDonors, or
CalcNumBasicNitrogens will each accept amide and anilinic nitrogens, which are not
protonated at pH 7.4 and cannot form the interaction. A library built on a leaky gate is a
library of compounds that cannot bind.

These tests pin the leaks shut.
"""

from __future__ import annotations

import pytest

pytest.importorskip("rdkit")

from rdkit import Chem, RDLogger

from veridian.chem.protonation import (
    can_reach_d332,
    cationic_n_indices,
    has_basic_nitrogen,
)

RDLogger.DisableLog("rdApp.*")


def mol(smiles: str) -> Chem.Mol:
    m = Chem.MolFromSmiles(smiles)
    assert m is not None, f"test fixture SMILES does not parse: {smiles}"
    return m


# --- nitrogens that ARE basic ---------------------------------------------------------

@pytest.mark.parametrize(
    ("name", "smiles"),
    [
        ("serotonin",   "C1=CC2=C(C=C1O)C(=CN2)CCN"),
        ("DMT",         "CN(C)CCC1=CNC2=CC=CC=C21"),
        ("mescaline",   "COC1=CC(=CC(=C1OC)OC)CCN"),
        ("primary amine",   "CCCN"),
        ("tertiary amine",  "CCN(CC)CC"),
        ("piperidine",      "C1CCNCC1"),
    ],
)
def test_basic_nitrogens_are_detected(name, smiles):
    assert has_basic_nitrogen(mol(smiles)), f"{name} should have a basic nitrogen"


# --- nitrogens that are NOT basic -- the leaks ----------------------------------------

@pytest.mark.parametrize(
    ("name", "smiles"),
    [
        ("acetamide",     "CC(=O)N"),
        ("benzamide",     "c1ccccc1C(=O)N"),
        ("sulfonamide",   "CS(=O)(=O)N"),
        ("aniline",       "Nc1ccccc1"),
        ("acetonitrile",  "CC#N"),
        ("nitrobenzene",  "[O-][N+](=O)c1ccccc1"),
        ("pyrrole",       "c1cc[nH]c1"),
    ],
)
def test_non_basic_nitrogens_are_rejected(name, smiles):
    assert not has_basic_nitrogen(mol(smiles)), f"{name} must NOT count as basic"


def test_molecule_with_no_nitrogen_has_none():
    assert not has_basic_nitrogen(mol("c1ccccc1O"))


def test_amide_plus_amine_finds_only_the_amine():
    """A molecule carrying both must report exactly one cationic centre."""
    indices = cationic_n_indices(mol("NCCC(=O)N"))
    assert len(indices) == 1


# --- the full gate: basic nitrogen AND reachable from the aromatic core ----------------

@pytest.mark.parametrize(
    ("name", "smiles"),
    [
        ("serotonin", "C1=CC2=C(C=C1O)C(=CN2)CCN"),
        ("DMT",       "CN(C)CCC1=CNC2=CC=CC=C21"),
        ("psilocin",  "CN(C)CCC1=CNC2=C1C(=CC=C2)O"),
        ("mescaline", "COC1=CC(=CC(=C1OC)OC)CCN"),
        ("LSD",       "CCN(CC)C(=O)[C@H]1CN([C@@H]2CC3=CNC4=CC=CC(=C34)C2=C1)C"),
        ("lisuride",  "CCN(CC)C(=O)N[C@@H]1CN([C@@H]2CC3=CNC4=CC=CC(=C34)C2=C1)C"),
        ("tabernanthalog", "CN1CCC2=C(CC1)NC3=C2C=CC(=C3)OC"),
    ],
)
def test_every_reference_agonist_passes_the_gate(name, smiles):
    """No reference 5-HT2A agonist may be rejected by our own enumeration filter."""
    verdict = can_reach_d332(mol(smiles))
    assert verdict.passes, f"{name} was rejected: {verdict.reason}"


def test_gate_rejects_a_molecule_with_no_basic_nitrogen():
    verdict = can_reach_d332(mol("c1ccccc1C(=O)N"))
    assert not verdict.passes
    assert "no basic nitrogen" in verdict.reason


def test_gate_rejects_a_cation_too_far_from_the_aromatic_core():
    """A long aliphatic tether puts the cation out of reach of D155."""
    verdict = can_reach_d332(mol("c1ccccc1CCCCCCCCN"))
    assert not verdict.passes
    assert "window" in verdict.reason


def test_gate_fails_closed_on_an_unparseable_molecule():
    assert not can_reach_d332(None).passes


def test_verdict_always_explains_itself():
    for smiles in ("CCCN", "CC(=O)N", "c1ccccc1CCCCCCCCN"):
        assert can_reach_d332(mol(smiles)).reason
