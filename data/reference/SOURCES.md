# Reference set provenance

Every structure in `reference_set.csv` was resolved against PubChem on 2026-09-24 and
carries its CID and InChIKey. `tests/test_reference_set.py` recomputes each InChIKey from
the committed SMILES and fails on any mismatch.

## Why identifiers, never name search (ADR-013)

A ChEMBL name search for `2-bromo-LSD` returns **`[3H]LSD`** — tritiated LSD. Different
molecule, opposite behavioural label, and nothing about the result announces the
substitution. The reference set is what every downstream number is calibrated against, so
a silent swap here would quietly invalidate the entire project.

Verified failures of fuzzy name lookup on this compound set:

| Query | Returned | Correct? |
|---|---|---|
| `2-bromo-LSD` (ChEMBL) | `[3H]LSD` | **no** |
| `tabernanthalog` (ChEMBL) | not found | — |
| `zalsupindole` (ChEMBL) | not found | — |
| `IHCH-7086` (ChEMBL) | not found | — |
| `zalsupindole` (PubChem) | `AAZ-A-154` CID 154694212 | probably — see TODO |

## Open items

**REF010 zalsupindole — confidence: medium.** PubChem resolves `zalsupindole` to
AAZ-A-154 (CID 154694212). The synonym chain zalsupindole → AAZ-A-154 → DLX-001 is
consistent with the published Delix compound, but it was established by name lookup, which
is exactly the method this file warns about. A human should confirm the INN maps to this
structure against a primary source before any result depending on REF010 is reported.

**REF012 RS130-180 — BLOCKED.** Not resolvable by name in either database. Carried as an
explicit `not_resolved` row with a null SMILES rather than guessed. The structure should
be extracted from the 9AS9 entry's chemical component dictionary, which is authoritative,
rather than looked up.

## Label bases

- `human` — reported psychedelic effects (or their documented absence) in humans.
- `rodent_HTR` — mouse or rat head-twitch response.
- `rodent_DD` — drug discrimination. A related but distinct assay; weaker evidence.
- `inferred` — from chemotype or a related compound. Weakest; use `label_confidence: low`.

## Attribution

Structures from PubChem (NCBI). Bioactivity from ChEMBL (EMBL-EBI). Coordinates from the
RCSB PDB. Literature via PubMed; design after Kaplan et al., *Nature* 610:582–591 (2022),
doi:10.1038/s41586-022-05258-z.
