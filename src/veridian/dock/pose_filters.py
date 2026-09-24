"""Pose-level filters. Docking scores lie; pose geometry lies less.
"""

from __future__ import annotations


def filter_poses(df, config):
    """Apply geometric filters to docked poses.

    INPUTS:   Docking-results DataFrame, Config.
    OUTPUTS:  Filtered DataFrame with per-pose rejection reasons retained.
    ACCEPTS:  tests/test_pose_filters.py -- a pose lacking the D3.32 salt bridge is rejected;
               rejections carry a reason and are never silently dropped.
    EFFORT:   ~1 day.
    """

    raise NotImplementedError(
        "filter_poses is not implemented; see the docstring for its contract."
    )
