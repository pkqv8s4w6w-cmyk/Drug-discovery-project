"""The reference set is the ruler. If it is wrong, every downstream number is wrong.

ADR-013: SMILES are resolved by identifier, never by name search. A ChEMBL name search for
'2-bromo-LSD' returns [3H]LSD -- a different molecule with the opposite behavioural label.
These tests exist to catch exactly that class of silent substitution.
"""

from __future__ import annotations

import pytest

VALID_LABELS = {"hallucinogen", "non_hallucinogen"}
VALID_SOURCES = {"pubchem", "chembl", "pdb_ccd", "manual_from_paper", "not_public", "not_resolved"}


def test_reference_set_is_not_empty(reference_rows):
    assert len(reference_rows) >= 13


def test_compound_ids_unique(reference_rows):
    ids = [r["compound_id"] for r in reference_rows]
    assert len(ids) == len(set(ids))


def test_class_labels_valid(reference_rows):
    for row in reference_rows:
        assert row["class_label"] in VALID_LABELS, row["compound_id"]


def test_both_classes_populated(reference_rows):
    labels = [r["class_label"] for r in reference_rows]
    assert labels.count("hallucinogen") >= 6
    assert labels.count("non_hallucinogen") >= 7


def test_source_types_valid(reference_rows):
    for row in reference_rows:
        assert row["smiles_source_type"] in VALID_SOURCES, row["compound_id"]


def test_unresolved_rows_are_retained_not_dropped(reference_rows):
    """An unresolved structure must survive as an explicit gap, never be quietly removed."""
    gaps = {"not_public", "not_resolved"}
    unresolved = [r for r in reference_rows if r["smiles_source_type"] in gaps]
    for row in unresolved:
        assert row["smiles"] == "", f"{row['compound_id']} claims unresolved but carries a SMILES"
        assert row["notes"], f"{row['compound_id']} is unresolved without explanation"


def test_every_resolved_row_has_a_source_id(reference_rows):
    for row in reference_rows:
        if row["smiles_source_type"] in {"not_public", "not_resolved"}:
            continue
        assert row["smiles_source_id"], f"{row['compound_id']} has no source identifier"


def test_hard_pair_groups_present(reference_rows):
    """Gate criteria G6 and G7 depend on these groups existing."""
    groups: dict[str, list[str]] = {}
    for row in reference_rows:
        if row["hard_pair_group"]:
            groups.setdefault(row["hard_pair_group"], []).append(row["compound_id"])

    assert "ergoline_triad" in groups
    assert set(groups["ergoline_triad"]) == {"REF001", "REF007", "REF008"}


def test_ergoline_triad_has_opposite_labels(reference_rows):
    """LSD against lisuride and 2-bromo-LSD -- near-identical structures, opposite labels."""
    by_id = {r["compound_id"]: r for r in reference_rows}
    assert by_id["REF001"]["class_label"] == "hallucinogen"
    assert by_id["REF007"]["class_label"] == "non_hallucinogen"
    assert by_id["REF008"]["class_label"] == "non_hallucinogen"


@pytest.mark.parametrize(
    ("compound_id", "expected_inchikey"),
    [
        ("REF001", "VAYOSLLFUXYJDT-RDTXWAMCSA-N"),   # LSD
        ("REF007", "BKRGVLQUQGGVSM-KBXCAEBGSA-N"),   # lisuride
        ("REF008", "VKRAXSZEDRWLAG-SJKOYZFVSA-N"),   # 2-bromo-LSD, NOT [3H]LSD
        ("REF009", "FNGNYGCPNKZYOG-UHFFFAOYSA-N"),   # tabernanthalog
    ],
)
def test_committed_inchikeys_are_the_expected_compounds(
    reference_rows, compound_id, expected_inchikey
):
    """Golden values. A silent structure substitution changes the InChIKey."""
    by_id = {r["compound_id"]: r for r in reference_rows}
    assert by_id[compound_id]["inchikey"] == expected_inchikey


def test_smiles_parse_and_match_committed_inchikeys(reference_rows):
    """Every committed SMILES must actually produce its committed InChIKey."""
    rdkit = pytest.importorskip("rdkit")
    from rdkit import Chem, RDLogger

    RDLogger.DisableLog("rdApp.*")
    del rdkit

    mismatches = []
    for row in reference_rows:
        if not row["smiles"]:
            continue
        mol = Chem.MolFromSmiles(row["smiles"])
        if mol is None:
            mismatches.append(f"{row['compound_id']}: SMILES does not parse")
            continue
        computed = Chem.MolToInchiKey(mol)
        if computed != row["inchikey"]:
            mismatches.append(
                f"{row['compound_id']} ({row['name']}): committed {row['inchikey']}, "
                f"computed {computed}"
            )
    assert not mismatches, "reference set integrity failure:\n  " + "\n  ".join(mismatches)


def test_lsd_and_lisuride_are_nearly_identical(reference_rows):
    """The premise of hard pair G6: these differ by an amide-to-urea swap.

    If they were not this similar, separating them would not be the hard test it is.
    """
    pytest.importorskip("rdkit")
    from rdkit import Chem, DataStructs, RDLogger
    from rdkit.Chem import rdFingerprintGenerator

    RDLogger.DisableLog("rdApp.*")
    by_id = {r["compound_id"]: r for r in reference_rows}
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = [
        gen.GetFingerprint(Chem.MolFromSmiles(by_id[cid]["smiles"]))
        for cid in ("REF001", "REF007")
    ]
    similarity = DataStructs.TanimotoSimilarity(*fps)
    assert similarity > 0.4, (
        f"LSD/lisuride Tanimoto is {similarity:.2f}; the hard-pair premise assumes "
        "these are structurally close"
    )
