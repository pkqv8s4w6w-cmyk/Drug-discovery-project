"""Pose rendering with the D3.32 contact highlighted.
"""

from __future__ import annotations

from pathlib import Path


def render_pose(pose_path: Path, receptor, out_path: Path) -> Path:
    """Render a pose image showing the salt-bridge contact.

    INPUTS:   Pose file, PreparedReceptor, output path.
    OUTPUTS:  Path to a PNG with the D3.32 contact highlighted; the residue is resolved through
               structure.residues, so 5-HT2B images label D135 rather than D155 (ADR-003).
    ACCEPTS:  tests/test_pose_images.py -- a 5-HT2B pose image labels D135.
    EFFORT:   ~1 day.
    """

    raise NotImplementedError(
        "render_pose is not implemented; see the docstring for its contract."
    )
