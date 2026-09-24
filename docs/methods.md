# Methods

Narrative companion to `PREREGISTRATION.md` (what was committed) and `DECISIONS.md` (why).

## The question

5-HT2A agonists show antidepressant potential, but hallucinogenic effects limit their use.
Compounds including lisuride, 2-bromo-LSD, tabernanthalog, IHCH-7086, zalsupindole and
Kaplan et al.'s (R)-69/(R)-70 activate 5-HT2A without producing the psychedelic effect, so
the two properties are separable in principle.

Whether they are separable *computationally* is what this pipeline tests.

## Approach

After Kaplan et al., *Nature* 610:582–591 (2022): rather than screening a generic catalog,
enumerate a bespoke, synthesis-aware library around a chosen scaffold and dock that. Their
library was 75M tetrahydropyridines, giving 17 synthesized compounds, 4 low-micromolar
hits, and two optimized non-psychedelic agonists with antidepressant activity in mice at
1/40 the fluoxetine dose. VERIDIAN runs the same shape of pipeline at roughly a tenth the
scale.

## Scaffolds

Constrained and rigidified systems, because that is where the non-hallucinogenic compounds
actually appear. Structure verification (ADR-004) corrected an early misattribution:
tabernanthalog is an **azepinoindole** (C14H18N2O), not an isoquinuclidine — the
isoquinuclidine belongs to ibogaine, and tabernanthalog is what results from removing it.
IHCH-7086 is azepino-fused; zalsupindole is an isoDMT.

So the known non-hallucinogenic agonists cluster in azepinoindole, isoDMT and ergoline
space. Day-one enumeration is tetrahydro-β-carboline plus azepinoindole; reaction SMARTS
ship for five chemotypes so the choice is a config change.

## The hard constraint

Every enumerated molecule must retain a basic nitrogen capable of the D155 (D3.32) salt
bridge — an interaction conserved across serotonin and the other aminergic receptors. No
salt bridge, no agonist.

Implemented as an explicit SMARTS predicate plus a topological rule, because the obvious
naive checks accept amide and anilinic nitrogens, which are not protonated at pH 7.4 and
cannot form the interaction. `tests/test_basic_nitrogen.py` pins each leak shut.

## The three proxies

Hallucinogenicity cannot be docked for. VERIDIAN commits in advance to three explicitly
labeled proxies:

1. **HTR classifier** (ligand-based). Reports; never filters or ranks (ADR-008).
2. **Differential docking** — Δz across pocket families. An untested hypothesis, carried
   with a permutation null and an induced-fit control (ADR-006).
3. **5-HT2A partial agonism** — better populated and less confounded than HTR (ADR-007).

## Validation

The gate runs before any library is enumerated (ADR-001) and evaluates seven numeric
criteria fixed in advance. The two that matter are G6 and G7: lisuride and 2-bromo-LSD
must each rank as less hallucinogen-like than LSD. These are near-identical ergolines with
opposite labels — LSD and lisuride differ by a single amide-to-urea substitution. A method
that separates the broader reference set while failing the hard pairs is separating on
gross chemotype and has learned nothing.

Decoys are property-matched and, critically, **charge-matched** at pH 7.4. Every true
active is a cation, so unmatched decoys would make the salt-bridge filter look like genius.
Three decoy sets are reported separately and never pooled; the random set exists only to
quantify how much AUC an unmatched benchmark inflates.

## What would make this real

A calcium-flux assay and a rodent head-twitch study. Until then every output is a
hypothesis, and the report says so on page one.
