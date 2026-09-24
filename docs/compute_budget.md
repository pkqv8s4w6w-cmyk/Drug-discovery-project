# Compute budget

Measured assumption: **~30 s per ligand per core** (Vina 1.2.5, exhaustiveness 8, 22 Å box,
4–8 rotatable bonds, 2.1 GHz Xeon). Four concurrent single-threaded processes give
**~480 ligands/hour**.

`scripts/bench_dock.py` should be the first thing run in a new environment: it docks 20
reference ligands and writes the *measured* rate into the run manifest, after which every
estimate below uses the measured number rather than this one.

## The arithmetic

| Job | Core-seconds | Wall time, 4 cores |
|---|---|---|
| 60 ligands × 1 receptor | 1.8k | 7.5 min |
| 13 reference × 14 receptors | 25k | 1.8 h |
| 1,000 decoys × 9 receptors (one-time background) | 270k | 19 h |
| 2,000 × 1 receptor | 60k | 4.2 h |
| 10,000 × 1 receptor | 300k | 20.8 h |
| 100,000 × 1 receptor | 3.0M | 8.7 days |
| **1,000,000 × 1 receptor** | **30M** | **87 days** |
| 1,000,000 × 9 receptors | 270M | 2.1 years |

**1M brute-force is infeasible here by a factor of ~100.**

Aggressive tuning — QuickVina2 (~2.5×), exhaustiveness 4 (~2×), an 18 Å box (~1.4×) —
reaches ~4.3 s/ligand and ~12 days for 1M. It buys that speed by degrading pose quality,
and every signal this project depends on is pose-level: salt-bridge geometry, TM5/TM6
contacts, interaction fingerprints. That is the wrong thing to buy.

## Costs that also bite at scale

- **Conformer + PDBQT prep:** ~0.4 s/mol → 1M = 27.8 h on 4 cores. Library prep alone
  exceeds a night.
- **Enumeration:** ~0.5–1.5 ms/product → 1M ≈ 15–40 min. Cheap. Fine at full scale.
- **Disk:** 1M × 9 poses ≈ **25–40 GB against 30 GB free**. The runner must stream —
  parse, extract score and IFP, keep the top 3 gzipped, discard the rest.
- **RAM:** four Vina processes ≈ 1–2 GB. Not a constraint, provided the library is a
  chunked generator into parquet row groups rather than a list.

## Tiers

| Tier | Contents | Wall time |
|---|---|---|
| `smoke` | 13 reference + 47 matched decoys, 6WHA only | **7.5 min** |
| `gate` | redocks ×3 seeds, reference × 14 receptors, 1,000-decoy background × 9, 150 actives + 150 verified inactives | **~24 h** |
| `dev` | 2,000 enumerated vs 6WHA, top 10% × 8 comparators, 2B panel | **~9.6 h** |
| `full` | 1M enumerated / ~20k docked via active learning | **not run here** |

## Active learning (ADR-010)

How 1M gets screened at all. Dock a random 2,000; fit LightGBM on ECFP4 counts; predict
all 1M (~3 min); dock the next 1,500 by greedy/UCB acquisition; repeat ~6 rounds.
**~9,500 docked ≈ 0.95% of the library ≈ two nights.**

Published Deep Docking / MolPAL results recover roughly 60–90% of the true top-0.1% at ~1%
docked fraction. VERIDIAN measures its own recall against a held-out fully-docked random
2,000 rather than citing that range as if it applied here.

## If compute materialises

- **CPU fan-out:** 1M × ~15 s on modern vCPUs ≈ 4,170 vCPU-h. On ~1,000 vCPUs, **~4.5 h**;
  roughly **$60–250** on spot.
- **GPU (cheapest by far):** Vina-GPU / QuickVina2-GPU on a single A10G runs 50–100× a CPU
  core — 1M in **10–30 h for $10–30**. It would also make GNINA usable again.
- **University SLURM:** free. `runner.emit_jobspec` writes the array job.

`compute.dispatch` accepts `local | slurm | awsbatch` from day one, and every stage is
shardable, so scaling out is a config change rather than a rewrite.

## Determinism

Vina is only reproducible with `--cpu 1 --seed N`; with `--cpu > 1`, thread interleaving
changes results even at a fixed seed. The runner therefore launches four single-threaded
processes rather than one four-threaded process — which is also faster, so determinism
costs nothing (ADR-012). `config.validate()` rejects any other setting.
