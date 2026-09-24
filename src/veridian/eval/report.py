"""Gate evaluation and metric assembly.
"""

from __future__ import annotations

from pathlib import Path


def evaluate_gate(config) -> tuple[bool, dict]:
    """Evaluate all seven pre-registered gate criteria.

    INPUTS:   Resolved Config.
    OUTPUTS:  (passed, per-criterion results). Writes runs/gate/PASS only on a full pass; `make
               library` depends on that marker (ADR-001).
    ACCEPTS:  tests/test_gate.py -- a single failed criterion blocks the marker; thresholds are
               read from PREREGISTRATION.md and never from a mutable config.
    EFFORT:   ~1 day. Thresholds are fixed in advance; a failing gate is reported, not renegotiated.
    """

    raise NotImplementedError(
        "evaluate_gate is not implemented; see the docstring for its contract."
    )


def assemble_report(config, out_path: Path) -> Path:
    """Assemble every metric into runs/<id>/report.json.

    INPUTS:   Config, output path.
    OUTPUTS:  Report path. Includes the pre-registration drift check in its header.
    ACCEPTS:  tests/test_gate.py -- a drifted pre-registration hash surfaces as a header warning.
    EFFORT:   ~0.5 day.
    """

    raise NotImplementedError(
        "assemble_report is not implemented; see the docstring for its contract."
    )
