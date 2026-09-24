#!/usr/bin/env python3
"""Measure this machine's actual docking throughput.

Run this FIRST in any new environment. Every time estimate in docs/compute_budget.md is
built on an assumed ~30 s/ligand/core on a 2.1 GHz Xeon. That number will be wrong
somewhere else -- possibly by several fold -- and a tier that was designed to finish
overnight could instead run for a week.

This script docks a small set of reference ligands, measures the real rate, and writes it
into the run manifest so downstream estimates use the measured value rather than the
assumption.

    python scripts/bench_dock.py --n 20
"""

from __future__ import annotations

import argparse


def main() -> int:
    """Benchmark docking throughput and record it in the run manifest.

    INPUTS:   --n ligands to dock (default 20), --tier for the docking parameters.
    OUTPUTS:  measured seconds/ligand/core written to runs/<run_id>/manifest.json under
              `measured_dock_rate`, plus projected wall times for each tier.
    ACCEPTS:  tests/test_bench.py -- reports a positive rate and projects tier wall times
              that scale linearly with the measured rate; refuses to run without a
              docking binary rather than reporting a fabricated number.
    EFFORT:   ~0.5 day. Blocked on: dock.engines.VinaEngine.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=20, help="ligands to dock")
    parser.add_argument("--tier", default="smoke", help="tier supplying docking parameters")
    parser.parse_args()

    raise NotImplementedError(
        "bench_dock is not implemented; see the docstring for its contract. "
        "It depends on veridian.dock.engines.VinaEngine."
    )


if __name__ == "__main__":
    raise SystemExit(main())
