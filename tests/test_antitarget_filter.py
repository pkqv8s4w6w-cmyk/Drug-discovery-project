"""ADR-002: the 5-HT2B filter must reject agonism, not affinity.

5-HT2B agonism causes valvular heart disease, which ends clinical development, so it is a
hard rejection filter. But implemented naively on binding affinity, that filter deletes
lisuride and 2-bromo-LSD -- two of this project's own reference negatives. Both bind
5-HT2B tightly, as ergolines do, but both are antagonists or inverse agonists and neither
is valvulopathic.

A filter that rejects the compounds you calibrate against is measuring the wrong thing.
"""

from __future__ import annotations

import pytest


def test_reference_negatives_are_present_to_be_protected(reference_rows):
    by_id = {r["compound_id"]: r for r in reference_rows}
    for compound_id in ("REF007", "REF008"):
        assert by_id[compound_id]["class_label"] == "non_hallucinogen"


def test_antitarget_config_uses_agonism_not_affinity():
    """The config must encode the ADR-002 rule, independent of the implementation."""
    import yaml

    from veridian.config import CONFIG_DIR

    cfg = yaml.safe_load((CONFIG_DIR / "models" / "h2b_reg.yaml").read_text())

    assert cfg["endpoints"]["primary"] == "EC50", "2B rejection must key on functional agonism"
    assert cfg["endpoints"]["covariate"] == "Ki", "affinity is a covariate, never the filter"
    assert cfg["assay_filter"]["assay_mode"] == ["agonist"]
    assert "and_emax_pct_gt" in cfg["reject_rule"], "efficacy is required, not optional"
    assert "abstain" in cfg["flag_values"], "out-of-domain must abstain, not silently reject"


@pytest.mark.xfail(reason="predict_h2b_agonism is not implemented yet", strict=False)
def test_2b_filter_retains_reference_nonhallucinogens(reference_rows):
    """THE regression test named in ADR-002 and configs/models/h2b_reg.yaml.

    Lisuride and 2-bromo-LSD must never be rejected by the antitarget filter.
    """
    from veridian.ml.regressors import predict_h2b_agonism

    by_id = {r["compound_id"]: r for r in reference_rows}
    smiles = [by_id["REF007"]["smiles"], by_id["REF008"]["smiles"]]

    predictions = predict_h2b_agonism(None, smiles)
    assert list(predictions["h2b_flag"]) != ["reject", "reject"]
