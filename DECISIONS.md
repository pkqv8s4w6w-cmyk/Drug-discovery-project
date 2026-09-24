# Architecture Decision Record

Each entry: what was decided, why, and what it rejected. Newest last.

---

## ADR-001 — Validation runs before library enumeration, and the Makefile enforces it
**Date:** 2026-09-24 · **Status:** accepted

The original 8-step design numbered validation last, after building a 1–5M compound library.
That ordering risks spending months before learning the method doesn't work.

Reordered to `0 → 1 → 2 → 7(redock + enrichment) → 6(differential) → GATE → 3 → 4 → 5 → 8`.
`make library` depends on `runs/gate/PASS`, written only when all seven pre-registered criteria
pass. The gate costs roughly one day of compute and answers the whole scientific question.

**Rejected:** documenting the order in prose only. A convention that isn't enforced isn't a
convention.

---

## ADR-002 — 5-HT2B rejection uses predicted agonism, not affinity
**Date:** 2026-09-24 · **Status:** accepted

5-HT2B agonism causes valvular heart disease (norfenfluramine, pergolide, cabergoline), which
ends clinical development. The original design made 5-HT2B a hard rejection filter.

Implemented naively on **affinity**, that filter deletes lisuride and 2-bromo-LSD — two of this
project's own reference negatives. Both bind 5-HT2B tightly, as ergolines do, but both are
antagonists or inverse agonists and neither is valvulopathic. A filter that rejects the
compounds you are calibrating against is measuring the wrong thing.

Rule: `pred_2b_pec50 > 7 AND pred_2b_emax > 20%` of serotonin, trained on the 1,022 ChEMBL 2B
EC50 records restricted to agonist-mode assays. Emitted as
`h2b_flag ∈ {clear, watch, reject, abstain}` rather than a silent drop. Locked by
`tests/test_antitarget_filter.py::test_2b_filter_retains_reference_nonhallucinogens`.

Corollary: docking barely predicts 2B binding and cannot predict 2B *agonism*, so this decision
is ML-driven with docking as a secondary signal — the inverse of the original weighting.

---

## ADR-003 — D3.32 is resolved through a per-PDB map, never hardcoded
**Date:** 2026-09-24 · **Status:** accepted

The conserved orthosteric aspartate is **D155 in 5-HT2A but D135 in 5-HT2B**. Hardcoding `155`
makes the entire antitarget panel silently wrong — no crash, no warning, just meaningless
numbers.

`configs/receptors.yaml` carries a Ballesteros–Weinstein map per PDB entry with `auth_chain` and
`auth_seq_id`, validated against the actual structure at load time. Locked by
`tests/test_residue_mapping.py`.

---

## ADR-004 — Tabernanthalog is an azepinoindole, not an isoquinuclidine
**Date:** 2026-09-24 · **Status:** accepted

The original scaffold list described isoquinuclidines as "tabernanthalog's space." That is
incorrect, and it matters because it would have aimed day-one enumeration at the wrong chemistry.

Verified against PubChem this session: tabernanthalog is CID 146026994, C14H18N2O,
`CN1CCC2=C(CC1)NC3=C2C=CC(=C3)OC` — a tetrahydroazepino-indole. The isoquinuclidine belongs to
**ibogaine** (C20H26N2O); tabernanthalog is what results from deliberately removing it.
IHCH-7086 (CID 162421364) is also azepino-fused, and zalsupindole / AAZ-A-154 is an isoDMT.

So the known non-hallucinogenic agonists cluster in **azepinoindole, isoDMT and ergoline** space,
not isoquinuclidine space.

**Consequence:** day-one enumeration is tetrahydro-β-carboline + **azepinoindole**, replacing the
originally chosen isoquinuclidine. Reaction SMARTS ship for all five chemotypes (THβC,
azepinoindole, isoDMT, 2-aminotetralin, isoquinuclidine) so the choice is a config change.
Isoquinuclidine is retained as a coded route since ibogaine-like chemistry remains interesting —
it is simply not where tabernanthalog lives.

---

## ADR-005 — GNINA is out; smina/Vinardo + interaction fingerprints are the rescoring stack
**Date:** 2026-09-24 · **Status:** accepted

Verified this session: `github.com` releases return **403** through the environment proxy, and
**`gnina` is not present in conda-forge at all**. `vina` (1.2.5–1.2.7), `smina` (2020.12.10) and
`openbabel` are available from conda-forge; `autodock-vina 1.2.5` and `openbabel 3.1.1` from apt.
There is no working channel for GNINA here.

Default rescoring stack:
1. `smina --scoring vinardo` — same cost as Vina, different functional form.
2. **ProLIF interaction-fingerprint Tanimoto to the native crystal pose** — ~30 ms/pose, and it
   directly encodes the D3.32 salt bridge, TM5 extended-pocket and TM6 toggle contacts that this
   project's hypothesis is actually about.
3. A locally-trained LightGBM rescorer on `[IFP bits ⊕ Vina terms ⊕ Vinardo terms]`, trained on
   the gate run's own actives-vs-verified-inactives set.

This is not a downgrade. A generic CNN affinity score does not encode the specific contacts the
hypothesis concerns; an interaction fingerprint does. `GninaEngine` remains as a feature-flagged
interface stub for a future GPU environment.

---

## ADR-006 — Cross-structure comparison uses Δz against a shared decoy background
**Date:** 2026-09-24 · **Status:** accepted

Differential scoring compares scores across structures of differing resolution (2.5 Å for 7WC9,
3.47 Å for 9AS9) and differing pocket volume. Raw Vina score differences between them are
dominated by those artifacts, not by biology.

Every receptor gets the *same* 1,000-decoy background docked into it once (~19 h, cached
permanently). All cross-structure comparison uses robust z-scores (median / 1.4826·MAD — the
score distributions are left-skewed, so mean/SD is wrong). Compare Δz, never Δ(kcal/mol).

Two further controls, both cheap: `partial_delta_z` residualizes Δz on similarity to each
family's native ligand (removing the induced-fit confound), and a 1,000-fold permutation null
shuffles the family assignment across the 8 comparator structures. The permutation test re-uses
cached scores and costs nothing.

---

## ADR-007 — 5-HT2A partial agonism added as a co-primary proxy
**Date:** 2026-09-24 · **Status:** accepted

Low-Emax, Gq-biased, β-arrestin-sparing partial agonism is the leading mechanistic hypothesis for
non-hallucinogenicity — IHCH-7086 is a partial agonist. ChEMBL holds 1,456 5-HT2A EC50 records
plus Emax data, versus the ~100 hand-extractable HTR datapoints.

Better populated, better defined, and less confounded than the HTR classifier. Registered as a
co-primary proxy in `PREREGISTRATION.md` §2 rather than an afterthought.

---

## ADR-008 — The HTR classifier reports; it never filters or ranks
**Date:** 2026-09-24 · **Status:** accepted

Roughly 85% of any assemblable HTR corpus is phenethylamine or tryptamine. Coverage of
tetrahydro-β-carbolines, azepinoindoles, isoDMTs and 2-aminotetralins is approximately zero. The
library this project exists to build is therefore almost entirely outside the classifier's
applicability domain.

Filtering on it would either drop everything (nothing in domain) or retain compounds on the
strength of an out-of-domain extrapolation — worse than making no prediction at all.

So: HTR columns appear on every candidate with a conformal prediction set and an in-domain flag;
ranking is driven by docking, differential scoring and the affinity/efficacy models; AD coverage
is a headline number in the report; and the "HTR in-domain" sub-table is permitted to be empty.

**An empty table there is a publishable result, not a pipeline failure.** This tension — between
wanting a novel library and having a classifier that only understands old chemotypes — is the
project's central methodological difficulty, and the repository surfaces it rather than hiding it.

---

## ADR-009 — Conformal prediction is hand-rolled and class-conditional
**Date:** 2026-09-24 · **Status:** accepted

Mondrian (class-conditional) inductive conformal prediction, implemented in
`ml/conformal.py` (~40 lines).

Three reasons over MAPIE: its API churned between 0.8.x and 1.x, so a pin is fragile for a repo
meant to be re-run in a year; at N ≈ 150 marginal coverage would be satisfied almost entirely by
the majority class, so class-conditional coverage is required; and the nonconformity score,
calibration quantile and `n_cal` need to be visible in the output record. MAPIE is retained as a
cross-check in tests.

`min_achievable_alpha()` **raises** when the calibration set cannot support the configured α.
With ~20 negatives total, a calibration fold holds ~8, so achievable class-conditional coverage
is quantized in steps of ~11% and no claim tighter than ~89% coverage for the negative class is
meaningful. The repo fails loudly at the top of the run rather than printing a confident number
with a footnote.

---

## ADR-010 — Enumerate and dock are separate budgets, bridged by active learning
**Date:** 2026-09-24 · **Status:** accepted

"1–5M compounds" conflates two numbers. Enumeration is cheap (~15–40 min for 1M). Docking 1M at
~30 s/ligand on 4 cores is **87 days**.

Split into `library.n_target` (enumerate 1–5M) and `screen.n_dock_budget` (dock 10–20k).
Active learning bridges them: dock a random 2,000, fit LightGBM on ECFP4 counts, predict all 1M
(~3 min), dock the next batch by greedy/UCB acquisition, repeat ~6 rounds. ~9,500 docked ≈ 0.95%
of the library ≈ two nights.

Published Deep Docking / MolPAL results recover roughly 60–90% of the true top-0.1% at ~1% docked
fraction. VERIDIAN measures its own recall loss against a held-out fully-docked random 2,000
rather than citing someone else's number.

**Rejected:** buying speed via `exhaustiveness=4` and a smaller box. That reaches ~12 days for 1M
by degrading pose quality — and every signal this project depends on is pose-level.

---

## ADR-011 — Cheap filters run at enumeration time, not after docking
**Date:** 2026-09-24 · **Status:** accepted

The original design applied PAINS, SA score and property filters at step 5, after docking.
Running them before conformer generation is roughly 2× cheaper for no effort.

Order, cheapest first: basic-nitrogen SMARTS + cation-to-aryl topological rule → CNS property
window → PAINS/Brenk/NIH → InChIKey dedupe → Murcko scaffold diversity cap.

Note SA score is nearly redundant here: the library is one or two steps from purchasable building
blocks, so `n_synth_steps` + `bb_ids` is a stronger synthesizability statement than any learned
score. SA is kept as a sanity check, not a filter.

---

## ADR-012 — Vina runs single-threaded, four processes wide
**Date:** 2026-09-24 · **Status:** accepted

Vina is only reproducible with `--cpu 1 --seed N`. With `--cpu > 1`, thread interleaving changes
results even at a fixed seed, which breaks `tests/test_determinism.py`.

The runner launches 4 single-threaded processes rather than 1 four-threaded process. This also
gives better throughput, so determinism costs nothing here.

---

## ADR-013 — Reference SMILES are resolved by identifier, never by name search
**Date:** 2026-09-24 · **Status:** accepted

Verified failure mode: a ChEMBL name search for `2-bromo-LSD` returns **`[3H]LSD`** — a different
molecule with the opposite behavioral label. Fuzzy name matching on this compound set silently
returns wrong structures, and the reference set is what everything downstream is calibrated
against.

Every row in `reference_set.csv` carries `smiles_source_type` and `smiles_source_id` (a PubChem
CID), plus an InChIKey and molecular formula for verification. `tests/test_reference_set.py`
asserts every SMILES parses and its computed InChIKey matches the committed value.

Unresolvable structures are carried as explicit NA rows with `smiles_source_type = not_resolved`
rather than guessed. RS130-180 (REF012) is currently such a row; its structure should be
extracted from the 9AS9 chemical component dictionary, not looked up by name.
