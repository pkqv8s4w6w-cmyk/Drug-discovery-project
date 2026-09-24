<div align="center">

# VERIDIAN

**A structure-based discovery pipeline for non-hallucinogenic 5-HT2A agonists**

*veridical* — of a perception: corresponding to reality rather than illusion.
The clinical antonym of *hallucinatory*.

</div>

---

> **Status: framework / skeleton.** Structure, configuration, schemas, CLI and the written
> scientific commitments are in place. Every computation is a typed stub with an explicit
> contract. Nothing in this repository has produced a result yet, and nothing here has been
> tested in a wet lab.

---

## What this is

5-HT2A agonists show real antidepressant potential, but the hallucinogenic effect is a serious
barrier to use. A growing set of compounds — lisuride, 2-bromo-LSD, tabernanthalog, IHCH-7086,
zalsupindole, and Kaplan et al.'s (R)-69/(R)-70 — activate 5-HT2A without producing the
psychedelic effect, which means the two properties are separable in principle.

VERIDIAN asks whether they can be separated *computationally*: enumerate a bespoke,
synthesis-aware library around constrained scaffolds, dock it against 5-HT2A structures solved
with hallucinogenic and non-hallucinogenic ligands bound, and rank by the difference.

The design follows Kaplan et al., *Nature* 2022
([10.1038/s41586-022-05258-z](https://doi.org/10.1038/s41586-022-05258-z)), who docked a bespoke
75-million-compound tetrahydropyridine library, synthesized 17 compounds, got 4 low-micromolar
hits, and optimized to two non-psychedelic agonists with antidepressant activity in mice at 1/40
the fluoxetine dose. VERIDIAN runs the same *shape* of pipeline at roughly a tenth the scale.

**The output is a list of candidates worth testing. That is the entire claim.**

---

## Pipeline

```
  STEP 0   Pre-register the proxies ────────────► PREREGISTRATION.md (hashed into every run)
             │
  STEP 1   Build the reference set ────────────► 6 hallucinogens vs 7 non-hallucinogens
             │                                    the ruler for everything downstream
  STEP 2   Receptor prep + redocking ──────────► 16 PDB structures, D3.32 validated
             │                                    native ligands must redock < 2 Å
             ▼
  ╔══════ GATE ═══════════════════════════════════════════════════════════╗
  ║  Can this pipeline put lisuride and LSD on opposite sides?            ║
  ║  7 numeric criteria, fixed in advance. Fails → stop and report.       ║
  ╚═══════════════════════════════════════════════════════════════════════╝
             │ PASS
  STEP 3   Bespoke library enumeration ────────► RDKit reaction SMARTS over Enamine blocks
             │                                    hard constraint: basic N reaching D155
  STEP 4   Docking cascade ────────────────────► Vina fast pass → smina/Vinardo rescore
             │                                    pose filters, not just score cutoffs
  STEP 5   ML filters ─────────────────────────► 2A affinity · 2A Emax · 2B agonism · HTR
             │                                    conformal intervals, abstains out of domain
  STEP 6   Differential-pose scoring ──────────► Δz across pocket families + permutation null
             │
  STEP 8   Cluster, rank, report ──────────────► 20–50 candidates with full provenance
```

Validation (step 7) is not a final step — it sits at the gate, before any library is built.
See ADR-001.

---

## Quickstart

```bash
make setup                        # venv, pip deps, apt vina + openbabel
make test                         # suite green; one xfail is intentional (see below)
veridian --help                   # every stage
veridian config show --tier smoke # resolved, validated configuration
veridian smoke --dry-run          # walk the full stage graph without computing
```

`--dry-run` walks the entire pipeline and stops at the first unimplemented stage, naming the
stub and its contract. That is the intended behavior of this skeleton.

---

## Repository layout

| Path | What lives there |
|---|---|
| `PREREGISTRATION.md` | Step 0. Proxy definitions and the 7 numeric gate criteria. Frozen, hashed into every run manifest. |
| `DECISIONS.md` | ADR log. Every methodological choice, why it was made, and what it rejected. |
| `data/reference/` | The ruler. Hand-curated, committed, every SMILES sourced and cited. |
| `configs/` | Layered YAML. Tiers, receptors, reactions, filters, models. |
| `src/veridian/` | The package. |
| `structures/MANIFEST.yaml` | Per-PDB provenance: sha256, resolution, chain, box, mutations. |
| `runs/<run_id>/` | Per-run manifest, report, candidates, figures. Gitignored. |

---

## The reference set

Thirteen compounds with certain labels, plus serotonin as the efficacy reference. Every SMILES
was resolved against PubChem and carries its CID and InChIKey; none were typed from memory or
matched by fuzzy name search, which returns wrong molecules for several of these compounds.

**Hallucinogenic:** LSD · psilocin · DMT · mescaline · DOI · 25CN-NBOH
**Non-hallucinogenic, 5-HT2A-active:** lisuride · 2-bromo-LSD · tabernanthalog · zalsupindole ·
IHCH-7086 · 6-fluoro-DET · RS130-180

The set exists to answer one question on day one rather than day ninety: **can the pipeline put
lisuride and LSD on opposite sides?** Those two molecules differ by a single amide-to-urea swap
and have opposite behavioral labels. `tests/test_hard_pairs.py` asserts the separation and is
marked `xfail` — it fails today, and it stays visible in every test run as a standing reminder
of the project's central difficulty.

---

## Limitations

Read this section before believing any output.

1. **Nothing here has been tested in a wet lab.** Every output is a hypothesis for synthesis and
   assay. None of it is evidence of activity or safety.
2. **"Non-hallucinogenic" is a proxy, twice removed.** Rodent head-twitch response is a surrogate
   for the human psychedelic experience; a docking-derived Δz is a surrogate for that surrogate.
   Both are pre-registered, and both may be wrong.
3. **Differential docking is an untested hypothesis.** No published work establishes that pocket
   preference predicts hallucinogenicity. It is reported with a permutation null and a
   native-ligand-similarity control precisely because it is plausible rather than established.
4. **The reference set can kill the method but cannot confirm it.** n = 6 vs 7 gives an AUC
   confidence interval wider than most effects anyone would want to claim.
5. **The HTR classifier is the weakest link, and everything downstream would inherit its error —
   so it is not allowed downstream.** Its training corpus is ~80–140 compounds, ~85%
   phenethylamine/tryptamine, so essentially every compound this pipeline generates falls outside
   its applicability domain. It reports; it does not filter or rank.
6. **HTR labels are confounded with 5-HT2A potency.** A potency-only baseline is reported beside
   every structural model. If the structural model does not beat it, no signal was demonstrated.
7. **Docking scores are not binding affinities.** Vina correlates with experimental affinity at
   roughly r ≈ 0.4–0.5. It is decent at enrichment and poor at rank-ordering — the whole pipeline
   is built around that fact.
8. **Rigid receptors.** Induced fit, water networks and the Gq-coupled conformational ensemble
   are ignored. Differential docking is especially exposed here, since each structure's pocket is
   induced-fit to its own ligand.
9. **No free-energy calculation, no MD.** Neither fits the hardware.
10. **Hardware ceiling.** Brute-force docking of 1M compounds is ~87 days on 4 CPU cores. Full-scale
    results come from active learning over roughly a 1% docked fraction, with the measured recall
    loss reported — or from an external run.
11. **Scope.** Target engagement and selectivity triage only. Nothing about PK, metabolic
    stability, hERG, or in vivo efficacy.
12. **Legal and ethical.** Several reference compounds are controlled substances. This repository
    contains computational analysis of published structures and public bioactivity data only. It
    contains no synthetic procedures for any controlled substance, and the bespoke library is
    deliberately built around non-scheduled constrained scaffolds. Low-quality self-report label
    sources are flagged and excluded from headline results.

---

## Attribution

Structural data from the RCSB PDB. Bioactivity data from ChEMBL (EMBL-EBI). Compound structures
from PubChem (NCBI). Literature identified via PubMed; the design follows Kaplan et al.,
*Nature* 610:582–591 (2022), [10.1038/s41586-022-05258-z](https://doi.org/10.1038/s41586-022-05258-z).

## License

MIT for the code. Data sources carry their own terms — see `docs/data_provenance.md`.
