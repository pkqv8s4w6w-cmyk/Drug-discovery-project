# VERIDIAN — Pre-registration

**Status:** FROZEN as of 2026-09-24
**Version:** 1.0.0

This document is written *before* any screening data is generated. Its SHA-256 is recorded in
every run manifest VERIDIAN produces. If this file changes between the gate run and any
screening run, the generated report flags the mismatch in its header.

The purpose of pre-registering is narrow and specific: it stops the definition of success from
drifting toward whatever the pipeline happens to produce. Choosing the proxy after seeing the
scores is the single easiest way to generate a convincing list of compounds that means nothing.

---

## 1. What is being claimed, and what is not

VERIDIAN nominates **candidate compounds worth testing**. It does not discover drugs, and no
output of this pipeline is evidence that any compound is non-hallucinogenic, safe, or effective.

The scientific claim under test is narrow:

> Given a bespoke library of constrained, rigidified 5-HT2A ligands, can a structure-based
> pipeline enrich for compounds that resemble known non-hallucinogenic 5-HT2A agonists more
> than they resemble known hallucinogenic ones?

That is a claim about **enrichment against a reference set**, not about any individual molecule.

---

## 2. The definition of "non-hallucinogenic" used here

Hallucinogenicity in humans cannot be docked for, predicted from structure with any established
accuracy, or measured in silico. VERIDIAN therefore commits, in advance, to **two explicitly
labeled proxies**, and to reporting both as proxies everywhere they appear.

### Proxy A — ligand-based HTR classifier
A classifier trained on rodent head-twitch response (HTR) data, itself a surrogate for the human
psychedelic experience.

**Known weaknesses, stated up front:**
- HTR is a rodent behavioral correlate, not the human phenomenon.
- The assemblable training corpus is roughly 80–140 compounds with quantitative rodent HTR,
  of which only ~12–25 are true negatives.
- ~85% of that corpus is phenethylamine or tryptamine. The library VERIDIAN builds is, by
  construction, almost entirely **outside the classifier's applicability domain**.
- HTR magnitude is confounded with 5-HT2A potency and Emax.

**Committed consequence:** Proxy A is a **reporter, not a filter**. It never removes a compound
and never drives final ranking. See §5.

### Proxy B — differential docking
Each compound is scored against 5-HT2A structures solved with hallucinogenic ligands bound and,
separately, against structures solved with non-hallucinogenic ligands bound. Compounds are ranked
by the normalized difference (Δz).

**This is an untested hypothesis.** No published work establishes that pocket-conformation
preference predicts hallucinogenicity. It is registered here as a hypothesis precisely so that
a null result is reportable rather than quietly discarded.

### Proxy C — 5-HT2A partial agonism (secondary, added at ADR-007)
Predicted Emax / efficacy class. Low-Emax, Gq-biased, β-arrestin-sparing partial agonism is the
leading mechanistic hypothesis for non-hallucinogenicity (IHCH-7086 is a partial agonist).
ChEMBL holds far more data on this than anyone holds on HTR, and it is less confounded.
Registered as a **co-primary** proxy alongside Proxy B.

---

## 3. The reference set is a kill test, not a confirmation test

`data/reference/reference_set.csv` holds 6 hallucinogens and 7 non-hallucinogens (plus serotonin
as an efficacy reference).

**With n = 6 vs 7, a reference-set AUC carries a 95% bootstrap CI of roughly ±0.20–0.25.**
An observed AUC of 0.85 is not statistically distinguishable from 0.60. Therefore:

> **Passing the gate is necessary but never sufficient.** A passing gate licenses continuing the
> project. It does not license any claim that the method works.

Failing the gate, however, *is* informative — a method that cannot separate compounds whose
labels are certain will not separate compounds whose labels are unknown.

---

## 4. Numeric stopping rules (the gate)

The gate runs before any library is enumerated. `make library` depends on `runs/gate/PASS`,
which is written only if **all** of the following hold. These thresholds are fixed now.

| # | Criterion | Threshold |
|---|---|---|
| G1 | Native-ligand redocking, top-ranked pose, symmetry-corrected RMSD | < 2.0 Å for X-ray ≤ 2.8 Å; < 3.0 Å for cryo-EM ≥ 3.2 Å |
| G2 | Enrichment of ChEMBL 5-HT2A actives over **verified inactives** at 6WHA | EF@1% ≥ 5.0 |
| G3 | ROC AUC, actives vs property-matched decoys, lower bound of 95% bootstrap CI | > 0.60 |
| G4 | Reference-set separation (Δz, hallucinogen vs non-hallucinogen) AUC | ≥ 0.60 |
| G5 | Permutation null: observed Δz separation vs 1,000 family-shuffles | p < 0.05 |
| G6 | **Hard pair:** lisuride (REF007) must rank as less hallucinogen-like than LSD (REF001) | strict |
| G7 | **Hard pair:** 2-bromo-LSD (REF008) must rank as less hallucinogen-like than LSD (REF001) | strict |

**G6 and G7 are the criteria that matter.** LSD, lisuride and 2-bromo-LSD are near-identical
ergolines with opposite behavioral labels — LSD and lisuride differ by a single amide-to-urea
substitution. Any method that separates the reference set while failing G6/G7 is separating on
gross chemotype, not on the property of interest, and has learned nothing useful.

**If the gate fails:** the failure is reported. The thresholds are not adjusted to accommodate the
result. The permitted responses are (a) fix an identified technical defect and re-run, or
(b) report the negative result. Re-running after a threshold change voids the pre-registration
and must be recorded as such in `DECISIONS.md`.

---

## 5. Committed analysis rules

1. **HTR never filters.** `htr_*` columns are reported with a conformal prediction set and an
   in-domain flag. Ranking uses docking + differential + affinity/efficacy models only.
2. **AD coverage is a headline number.** The fraction of candidates inside the HTR classifier's
   applicability domain appears on page one of every report. The "HTR in-domain" sub-table is
   permitted to be empty; an empty table is a valid result, not a pipeline failure.
3. **A potency-only baseline is reported next to every structural model.** If a structural model
   does not beat logistic regression on `[pEC50_2A, emax_2A]` alone by more than its own CV
   spread, the report states that no hallucinogenicity signal was demonstrated.
4. **Three decoy sets, reported separately, never pooled:** verified ChEMBL inactives (primary),
   property-matched decoys (charge-matched at pH 7.4), and random background. The random set
   exists only to quantify how much AUC an unmatched benchmark inflates.
5. **Cross-structure comparisons use Δz, never Δ(kcal/mol).** Per-receptor robust normalization
   (median/MAD) against a shared decoy background docked into every receptor.
6. **Δz is reported alongside `partial_delta_z`** (residualized on similarity to each family's
   native ligand) and a permutation p-value. A Δz that does not survive the permutation null is
   flagged on the compound.
7. **5-HT2B rejection is based on predicted agonism, not affinity.** Threshold:
   `pred_2b_pec50 > 7 AND pred_2b_emax > 20%` of serotonin. Emitted as
   `h2b_flag ∈ {clear, watch, reject, abstain}`. Rationale: lisuride and 2-bromo-LSD bind 5-HT2B
   tightly but are antagonists/inverse agonists and are not valvulopathic — an affinity-based
   filter would delete two of this project's own reference negatives.
8. **Nothing is silently dropped or silently promoted.** Every candidate carries a `flags` column
   listing its caveats, and the flags are printed in the report.

---

## 6. Final output specification

20–50 compounds, clustered by scaffold so the list is not 40 near-identical analogs. Each carries:
dock score against both pocket families, predicted 2A affinity and Emax, predicted 2B agonism
with its flag, HTR classifier output with conformal set and in-domain flag, a pose image showing
the D155 contact, nearest ChEMBL neighbor with Tanimoto, and one sentence of rationale.

Every report states, in its own header: **no compound in this list has been synthesized or
assayed, and none of these predictions constitutes evidence of activity or safety.**

---

## 7. Scope exclusions

VERIDIAN says nothing about pharmacokinetics, metabolic stability, hERG liability, off-target
selectivity beyond the modeled panel, or in vivo efficacy. It is a target-engagement and
selectivity triage tool. Candidate lists are hypotheses for a calcium-flux assay and, eventually,
a rodent HTR study — which is where the actual answer comes from.
