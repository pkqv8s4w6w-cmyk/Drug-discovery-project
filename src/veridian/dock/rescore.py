"""Rescoring stack (ADR-005): Vinardo, then IFP Tanimoto to the native pose, then a
locally-trained rescorer. GNINA is optional and unavailable here.
"""

from __future__ import annotations

from pathlib import Path


def rescore_poses(poses_path: Path, receptor, config):
    """Apply the configured rescoring stack to surviving poses.

    INPUTS:   Pose file, PreparedReceptor, Config.
    OUTPUTS:  DataFrame: vinardo score, ifp_tanimoto_to_native, learned rescorer output.
    ACCEPTS:  tests/test_rescore.py -- the native pose scores best on ifp_tanimoto_to_native by
               construction; a decoy pose does not.
    EFFORT:   ~1 day.
    """

    raise NotImplementedError(
        "rescore_poses is not implemented; see the docstring for its contract."
    )


def train_local_rescorer(gate_results, config):
    """Train a LightGBM rescorer on the gate run's own docked actives and verified inactives.

    INPUTS:   Gate docking results, Config.
    OUTPUTS:  Fitted model over [IFP bits + vina terms + vinardo terms].
    ACCEPTS:  tests/test_rescore.py -- beats raw vina score on held-out gate data, or the report
               says it does not and the raw score is used instead.
    EFFORT:   ~1 day. Target-specific and validated on our own data rather than on PDBbind.
    """

    raise NotImplementedError(
        "train_local_rescorer is not implemented; see the docstring for its contract."
    )
