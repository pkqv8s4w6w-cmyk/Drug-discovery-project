# Working in this repository

## Read first
`PREREGISTRATION.md` (what was committed, before data) and `DECISIONS.md` (why, and what
it rejected). Most non-obvious choices here are deliberate and recorded.

## Rules that are not style preferences

1. **Never hardcode a residue number.** D3.32 is D155 in 5-HT2A and **D135** in 5-HT2B.
   Resolve through `veridian.structure.residues`. Hardcoding does not crash; it silently
   produces meaningless numbers (ADR-003).
2. **Never resolve a compound by name search.** A ChEMBL search for `2-bromo-LSD` returns
   `[3H]LSD`. Use identifiers, and verify the InChIKey (ADR-013).
3. **Never compare raw docking scores across receptors.** Use `score_z` (ADR-006).
4. **Never let the HTR classifier filter or rank.** It reports (ADR-008).
5. **Never filter 5-HT2B on affinity.** Agonism only — an affinity filter deletes lisuride
   and 2-bromo-LSD from our own reference set (ADR-002).
6. **Never set `vina_cpu_per_process` above 1.** Vina is non-deterministic with `--cpu > 1`
   even at a fixed seed (ADR-012). `config.validate()` rejects it.
7. **Never adjust a gate threshold to make a run pass.** Thresholds are pre-registered. A
   failing gate is reported. Changing one voids the pre-registration and must be recorded
   in `DECISIONS.md`.
8. **Never delete `tests/test_hard_pairs.py`.** It is xfail on purpose and is the only
   check distinguishing this project from an expensive similarity search.

## Stub contract

Every stub raises `NotImplementedError` and its docstring carries `INPUTS:`, `OUTPUTS:`,
`ACCEPTS:` and `EFFORT:`. `tests/test_stubs.py` enforces this. When implementing one,
satisfy the acceptance test named in `ACCEPTS:` and remove the raise — do not loosen the
contract.

## Commands

    make setup      venv, deps, docking binaries
    make test       suite (3 xfails are intentional)
    make lint       ruff, must be clean
    veridian smoke --dry-run

## Environment facts (verified 2026-09-24)

- 4 cores, 15 GiB RAM, no GPU. 1M-compound brute-force docking is ~87 days — see
  `docs/compute_budget.md` before promising any full-scale run.
- `github.com` releases return **403** through the proxy, and `gnina` is absent from
  conda-forge. GNINA is unavailable; the rescoring stack is smina/Vinardo plus interaction
  fingerprints (ADR-005).
- `vina`, `smina`, `openbabel` install from conda-forge; `autodock-vina` and `openbabel`
  from apt.
- ChEMBL, RCSB and PubChem APIs are all reachable.

## Honesty conventions

Negative results are results. An empty "HTR in-domain" table, a Δz that does not survive
the permutation null, a structural model that fails to beat the potency-only baseline —
each is reported plainly rather than worked around. The `flags` column on every candidate
exists so nothing is silently dropped or silently promoted.
