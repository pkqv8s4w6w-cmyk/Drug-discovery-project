"""Protein-ligand interaction fingerprints via ProLIF.

At ~30 ms/pose this is nearly free, and it encodes exactly the contacts this project's
hypothesis concerns -- the D3.32 salt bridge, the TM5 extended pocket, the TM6 toggle.
That is why it outranks a generic CNN affinity score in the rescoring stack (ADR-005).
"""

from __future__ import annotations

from pathlib import Path


def interaction_fingerprint(pose_path: Path, receptor, config):
    """Compute the ProLIF interaction fingerprint for a pose.

    INPUTS:   Pose file, PreparedReceptor, Config.
    OUTPUTS:  Bit vector plus named contacts at the mapped BW positions.
    ACCEPTS:  tests/test_interactions.py -- the native 6WHA pose shows a D155 salt bridge; contact
               positions resolve through structure.residues, never hardcoded numbers.
    EFFORT:   ~1 day.
    """

    raise NotImplementedError(
        "interaction_fingerprint is not implemented; see the docstring for its contract."
    )


def salt_bridge_distance(pose, receptor) -> float:
    """Minimum distance from any ligand cation to the D3.32 carboxylate.

    INPUTS:   Pose, PreparedReceptor.
    OUTPUTS:  Distance in Angstrom (inf when no cationic atom is present).
    ACCEPTS:  tests/test_interactions.py -- D3.32 resolves per-target (D155 vs D135) via ADR-003.
    EFFORT:   ~4 h.
    """

    raise NotImplementedError(
        "salt_bridge_distance is not implemented; see the docstring for its contract."
    )
