"""Native-ligand redocking -- gate criterion G1.

If native ligands do not reproduce their crystallographic poses, nothing downstream means
anything, and the failure is a preparation bug rather than a scientific result.

Thresholds are resolution-aware (PREREGISTRATION G1): < 2.0 A for X-ray <= 2.8 A, but
< 3.0 A for cryo-EM >= 3.2 A. At 3.4 A the deposited ligand coordinates themselves carry
about 1 A of uncertainty, so a flat 2 A threshold would send you chasing a phantom.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RedockResult:
    pdb_id: str
    top_pose_rmsd: float
    best_pose_rmsd: float
    threshold: float
    passed: bool



def redock_native(pdb_id: str, config, seeds: tuple[int, ...] = (1, 2, 3)) -> RedockResult:
    """Redock the native ligand into its own structure across several seeds.

    INPUTS:   PDB id, Config, RNG seeds.
    OUTPUTS:  RedockResult with symmetry-corrected RMSD. top_pose_rmsd is the honest number and is
               what the gate uses; best_pose_rmsd is reported alongside it.
    ACCEPTS:  tests/test_redock.py -- symmetry-equivalent atoms do not inflate RMSD (use spyrmsd or
               RDKit GetBestRMS, never a naive atom-order comparison).
    EFFORT:   ~1 day.
    """

    raise NotImplementedError(
        "redock_native is not implemented; see the docstring for its contract."
    )
