"""Report rendering.

Two things appear on page one of every report: the applicability-domain coverage fraction,
and the statement that no compound in the list has been synthesised or assayed.
"""

from __future__ import annotations

from pathlib import Path


def render_html(config, metrics: dict, candidates, out_path: Path) -> Path:
    """Render the run report.

    INPUTS:   Config, metric dict, candidate DataFrame, output path.
    OUTPUTS:  Path to report.html. Headline AD coverage on page one; the 'HTR in-domain' sub-table
               may legitimately be empty; per-compound flags are printed, never hidden.
    ACCEPTS:  tests/test_render.py -- an empty in-domain table renders as a valid result with an
               explanation, not as an error.
    EFFORT:   ~1 day.
    """

    raise NotImplementedError(
        "render_html is not implemented; see the docstring for its contract."
    )
