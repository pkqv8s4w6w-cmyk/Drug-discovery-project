# HTR corpus extraction

`htr_corpus.csv` must be hand-extracted from primary literature. There is no curated
public head-twitch-response dataset — PubMed searches on 2026-09-24 confirmed the data is
scattered across individual papers.

This file is the work queue. One row per compound, one PMID per row.

## Expected yield, honestly

| Source | Compounds | Label quality |
|---|---|---|
| Halberstadt & Geyer mouse HTR series (2011–2021): substituted phenethylamines (2C-x, DOx, NBOMe/NBOH), 4-substituted and N,N-dialkyl tryptamines | 60–120 | high — quantitative ED50 / max HTR |
| Glennon DOM drug-discrimination corpus | +80–150 | medium — different assay, correlated not identical |
| Non-hallucinogenic-agonist papers: Olson lab (tabernanthalog, AAZ-A-154, DLX-001), Cheng/Wang (IHCH-7079/7086/7113), Kaplan 2022, Nichols (lisuride) | +15–30 | high — **the only negatives that matter** |
| PiHKAL / TiHKAL | +~230 | **low** — self-experimentation, not peer-reviewed, dose-range only |

**Tier A (quantitative rodent HTR only): N ≈ 80–140, with only ~12–25 true negatives.**
Tier B adds drug discrimination (N ≈ 200–280). Tier C adds self-report (N ≈ 350–450) and
is **never used in headline results**.

## Two facts to record, not bury

**Chemical coverage.** Roughly 85% of the corpus is phenethylamine or tryptamine. Coverage
of tetrahydro-β-carbolines, azepinoindoles, isoDMTs, 2-aminotetralins and
aminomethylchromanes is approximately zero — which is to say, of everything this project
enumerates. `data/htr_corpus.chemotype_coverage()` reports this directly. It is the
finding, not a bug (ADR-008).

**The potency confound.** HTR magnitude tracks 5-HT2A potency and Emax, and most
HTR-negatives are also weak or partial agonists. Restrict the primary corpus to compounds
with a measured 5-HT2A agonist EC50 and carry pEC50/Emax as explicit covariates, so the
model has to find signal beyond potency. The potency-only baseline in `ml/baselines.py`
makes the comparison unavoidable.

## Schema

    compound_id, name, smiles, inchikey, smiles_source_type, smiles_source_id,
    htr_label (positive|negative), htr_ed50_mg_kg, htr_max_response, species, strain,
    assay_type (HTR|DD), label_quality (A|B|C), pchembl_2a, emax_2a, chemotype,
    pmid, doi, curator, curated_at, notes

## Rules

1. One PMID per row. A row without a citation does not go in.
2. Never infer a negative from absence of data. "Not reported" is not "no response."
3. Record species and strain — HTR potency varies between them.
4. Tier C rows are loaded only on explicit request and never reach a headline number.
5. Resolve structures by identifier, never by name search (ADR-013).
