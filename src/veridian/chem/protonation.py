"""Basic-nitrogen detection and the D3.32 salt-bridge capability gate.

The hard constraint on library enumeration: every molecule must retain a basic nitrogen
able to form the salt bridge to D155 (D3.32). That ionic interaction is conserved across
serotonin and the other aminergic receptors. No salt bridge, no agonist.

This is implemented as an explicit SMARTS predicate plus a topological rule rather than as
a heuristic, because the obvious naive versions leak. `Chem.Lipinski.NumHDonors`,
`rdMolDescriptors.CalcNumBasicNitrogens`, or a bare `[N]` match will all happily accept
amide and anilinic nitrogens, which are not protonated at pH 7.4 and cannot form the salt
bridge. A library built on a leaky gate is a library of compounds that cannot bind.
"""

from __future__ import annotations

from dataclasses import dataclass

from rdkit import Chem

# A nitrogen that is genuinely basic at physiological pH.
# Each exclusion is deliberate:
#   !$(N[C,S,P]=[O,S,N])  amides, sulfonamides, phosphoramides -- delocalised, not basic
#   !$(N[a])              anilines -- lone pair into the ring, pKa ~4.6
#   !$(N#*)               nitriles
#   !$([N+])              already-quaternised nitrogen cannot accept a proton
#   !$(N=*)               imines and azo nitrogens
#   !$(N[N,O])            hydrazines, hydroxylamines -- alpha-effect depresses basicity
BASIC_N_SMARTS = (
    "[NX3;H2,H1,H0;"
    "!$(N[C,S,P]=[O,S,N]);"
    "!$(N[a]);"
    "!$(N#*);"
    "!$([N+]);"
    "!$(N=*);"
    "!$(N[N,O])]"
)

# Amidines and guanidines are strongly basic and pass despite the N=* exclusion above.
AMIDINE_SMARTS = "[NX3][CX3]=[NX2]"
GUANIDINE_SMARTS = "[NX3][CX3](=[NX2])[NX3]"

# Topological window between the cationic centre and the nearest aromatic ring atom.
# Derived from the reference agonists: serotonin, tryptamines and phenethylamines all
# place the cation 2-3 bonds from the aryl system; the ergoline ring N sits at 3-4.
MIN_BONDS_TO_AROMATIC = 2
MAX_BONDS_TO_AROMATIC = 4

_BASIC_N = Chem.MolFromSmarts(BASIC_N_SMARTS)
_AMIDINE = Chem.MolFromSmarts(AMIDINE_SMARTS)
_GUANIDINE = Chem.MolFromSmarts(GUANIDINE_SMARTS)


@dataclass(frozen=True)
class SaltBridgeVerdict:
    """Why a molecule passed or failed the gate. The reason is kept for auditability."""

    passes: bool
    reason: str
    cationic_atom_indices: tuple[int, ...] = ()
    bond_distance_to_aromatic: int | None = None


def cationic_n_indices(mol: Chem.Mol) -> list[int]:
    """Atom indices of nitrogens expected to be protonated at pH 7.4."""
    if mol is None:
        return []
    found: set[int] = set()
    for pattern in (_BASIC_N, _AMIDINE, _GUANIDINE):
        if pattern is None:
            continue
        for match in mol.GetSubstructMatches(pattern):
            found.add(match[0])
    return sorted(found)


def has_basic_nitrogen(mol: Chem.Mol) -> bool:
    """True when the molecule carries at least one genuinely basic nitrogen."""
    return bool(cationic_n_indices(mol))


def _min_bonds_to_aromatic(mol: Chem.Mol, atom_idx: int) -> int | None:
    """Shortest bond path from `atom_idx` to any aromatic ring atom, or None if unreachable."""
    aromatic = [a.GetIdx() for a in mol.GetAtoms() if a.GetIsAromatic()]
    if not aromatic:
        return None
    distances = [
        len(Chem.GetShortestPath(mol, atom_idx, target)) - 1
        for target in aromatic
        if target != atom_idx
    ]
    valid = [d for d in distances if d > 0]
    return min(valid) if valid else None


def can_reach_d332(
    mol: Chem.Mol,
    min_bonds: int = MIN_BONDS_TO_AROMATIC,
    max_bonds: int = MAX_BONDS_TO_AROMATIC,
) -> SaltBridgeVerdict:
    """Gate a molecule on its ability to form the conserved D3.32 salt bridge.

    Two requirements: a basic nitrogen, and that nitrogen positioned within a plausible
    topological window of the aromatic system that occupies the orthosteric pocket.

    This is a necessary-condition filter, not a prediction. It rejects molecules that
    cannot possibly make the interaction; it does not claim the survivors will.

    Args:
        mol: an RDKit molecule. `None` fails closed.
        min_bonds: minimum bonds from cation to nearest aromatic atom.
        max_bonds: maximum bonds.

    Returns:
        A `SaltBridgeVerdict` carrying the decision and its reason.
    """
    if mol is None:
        return SaltBridgeVerdict(False, "unparseable molecule")

    indices = cationic_n_indices(mol)
    if not indices:
        return SaltBridgeVerdict(False, "no basic nitrogen")

    best: int | None = None
    passing: list[int] = []
    for idx in indices:
        distance = _min_bonds_to_aromatic(mol, idx)
        if distance is None:
            continue
        if best is None or distance < best:
            best = distance
        if min_bonds <= distance <= max_bonds:
            passing.append(idx)

    if not passing:
        if best is None:
            return SaltBridgeVerdict(False, "no aromatic system reachable from a basic nitrogen")
        return SaltBridgeVerdict(
            False,
            f"basic nitrogen is {best} bonds from the nearest aromatic atom, "
            f"outside the {min_bonds}-{max_bonds} window",
            tuple(indices),
            best,
        )

    return SaltBridgeVerdict(
        True, "basic nitrogen within reach of aromatic core", tuple(passing), best
    )


def dominant_microstate(smiles: str, ph: float = 7.4) -> str:
    """Return the dominant protonation microstate at the given pH.

    INPUTS:   SMILES string, target pH.
    OUTPUTS:  SMILES of the dominant microstate, with formal charges assigned.
    ACCEPTS:  tests/test_protonation.py -- serotonin, DMT and lisuride each return a
              singly-protonated cation at pH 7.4; an amide-only molecule returns neutral.
    EFFORT:   ~0.5 day. Wrap dimorphite-dl. Blocked on: nothing.
    """
    raise NotImplementedError(
        "dominant_microstate is not implemented; wrap dimorphite-dl. "
        "See docstring for the acceptance test."
    )


def estimate_basic_pka(mol: Chem.Mol) -> float | None:
    """Rule-based estimate of the most basic pKa, or None when no rule applies.

    INPUTS:   RDKit molecule.
    OUTPUTS:  estimated pKa of the most basic centre, or None (meaning "unknown", which
              must propagate as unknown rather than being silently coerced to a default).
    ACCEPTS:  tests/test_protonation.py -- returns 9-11 for a primary aliphatic amine,
              8-10 for a tertiary amine, and None for an amide-only molecule.
    EFFORT:   ~1 day for a rule table. Blocked on: nothing.
    """
    raise NotImplementedError("estimate_basic_pka is not implemented; see docstring.")
