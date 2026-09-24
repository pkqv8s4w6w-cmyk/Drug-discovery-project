"""Ballesteros-Weinstein residue resolution.

ADR-003. The conserved orthosteric aspartate D3.32 is residue **155 in 5-HT2A** and
residue **135 in 5-HT2B**. Hardcoding 155 does not crash against a 5-HT2B structure -- it
silently selects the wrong residue, and every pose filter, salt-bridge distance and
interaction fingerprint computed against the antitarget panel becomes meaningless while
looking entirely normal.

So no module anywhere in VERIDIAN writes a residue number as a literal. Residues are
resolved through the per-PDB map in `configs/receptors.yaml` and validated against the
deposited structure at load time, where a mismatch is a hard error.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from veridian.config import load_receptors

_RESIDUE_RE = re.compile(r"^([A-Z])(\d+)$")

# Three-letter to one-letter, for checking a map entry against a deposited residue name.
THREE_TO_ONE: dict[str, str] = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


class ResidueMappingError(ValueError):
    """Raised when a BW number cannot be resolved, or resolves to the wrong residue."""


@dataclass(frozen=True)
class ResidueRef:
    """A concrete residue in a concrete structure."""

    pdb_id: str
    bw: str
    one_letter: str
    seq_id: int
    chain: str

    def __str__(self) -> str:
        return f"{self.one_letter}{self.seq_id}[{self.bw}] chain {self.chain} of {self.pdb_id}"


def _parse_entry(entry: str) -> tuple[str, int]:
    """Split a map value like 'D155' into ('D', 155)."""
    match = _RESIDUE_RE.match(entry.strip().upper())
    if not match:
        raise ResidueMappingError(
            f"malformed residue entry {entry!r}; expected a one-letter code "
            f"followed by a sequence number, e.g. 'D155'"
        )
    return match.group(1), int(match.group(2))


def resolve(pdb_id: str, bw: str, receptors: dict[str, Any] | None = None) -> ResidueRef:
    """Resolve a Ballesteros-Weinstein number to a concrete residue.

    Args:
        pdb_id: e.g. "6WHA".
        bw: e.g. "3.32".
        receptors: parsed receptors.yaml; loaded if omitted.

    Returns:
        The resolved `ResidueRef`.

    Raises:
        ResidueMappingError: unknown structure, unknown target, or unmapped BW number.
    """
    panel = receptors or load_receptors()
    entry = panel.get("receptors", {}).get(pdb_id.upper())
    if entry is None:
        raise ResidueMappingError(f"{pdb_id} is not in the receptor panel")

    target = entry.get("target")
    bw_map = panel.get("bw_maps", {}).get(target)
    if bw_map is None:
        raise ResidueMappingError(f"no Ballesteros-Weinstein map for target {target!r}")

    if bw not in bw_map:
        raise ResidueMappingError(
            f"BW {bw} is not mapped for {target}; mapped positions: {sorted(bw_map)}"
        )

    one_letter, seq_id = _parse_entry(str(bw_map[bw]))
    return ResidueRef(
        pdb_id=pdb_id.upper(),
        bw=bw,
        one_letter=one_letter,
        seq_id=seq_id,
        chain=str(entry.get("auth_chain", "A")),
    )


def orthosteric_aspartate(pdb_id: str, receptors: dict[str, Any] | None = None) -> ResidueRef:
    """Resolve D3.32 for a structure -- D155 in 5-HT2A, D135 in 5-HT2B.

    Raises:
        ResidueMappingError: if the mapped residue is not an aspartate, which would mean
            the map itself is wrong.
    """
    ref = resolve(pdb_id, "3.32", receptors)
    if ref.one_letter != "D":
        raise ResidueMappingError(
            f"{pdb_id} maps BW 3.32 to {ref.one_letter}{ref.seq_id}, not an aspartate. "
            f"The conserved orthosteric anchor must be Asp; the map is wrong."
        )
    return ref


def key_residues(pdb_id: str, receptors: dict[str, Any] | None = None) -> dict[str, ResidueRef]:
    """Every mapped BW position for a structure, keyed by BW number."""
    panel = receptors or load_receptors()
    entry = panel.get("receptors", {}).get(pdb_id.upper())
    if entry is None:
        raise ResidueMappingError(f"{pdb_id} is not in the receptor panel")
    bw_map = panel.get("bw_maps", {}).get(entry.get("target"), {})
    return {bw: resolve(pdb_id, bw, panel) for bw in bw_map}


def assert_key_residues(pdb_id: str, observed: dict[int, str], chain: str | None = None) -> None:
    """Verify the map against residues actually present in the deposited structure.

    Author numbering can differ from UniProt numbering because of fusion partners,
    truncations and renumbering, so the map in `receptors.yaml` is an assertion to be
    checked, not a fact to be trusted. Entries in the panel carry `verify: true` until
    this check has confirmed them.

    Args:
        pdb_id: structure being validated.
        observed: `{auth_seq_id: three_letter_resname}` read from the structure.
        chain: chain checked, for the error message.

    Raises:
        ResidueMappingError: listing every mismatch at once, so a bad map is fixed in a
            single pass rather than one residue per run.
    """
    problems: list[str] = []
    for bw, ref in key_residues(pdb_id).items():
        resname = observed.get(ref.seq_id)
        if resname is None:
            problems.append(f"BW {bw}: residue {ref.seq_id} absent from the structure")
            continue
        actual = THREE_TO_ONE.get(resname.upper())
        if actual != ref.one_letter:
            problems.append(
                f"BW {bw}: map says {ref.one_letter}{ref.seq_id}, structure has "
                f"{resname.upper()}{ref.seq_id}"
            )

    if problems:
        where = f"{pdb_id} chain {chain}" if chain else pdb_id
        raise ResidueMappingError(
            f"residue map does not match the deposited structure for {where}:\n  "
            + "\n  ".join(problems)
            + "\nFix configs/receptors.yaml before docking; every pose filter and "
            "interaction fingerprint depends on these positions (ADR-003)."
        )
