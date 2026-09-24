"""Docking engine adapters behind one Protocol.

ADR-005: GNINA has no reachable distribution channel in this environment -- github.com
returns 403 through the proxy and gnina is absent from conda-forge entirely. GninaEngine
is therefore an interface stub, feature-flagged off. Vina (apt and conda-forge) and smina
(conda-forge) are the working engines.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class DockResult:
    ligand_id: str
    scores: tuple[float, ...]
    poses_path: Path
    runtime_s: float


class DockEngine(Protocol):
    name: str
    version: str

    def dock(self, ligand_pdbqt: Path, receptor, box, *, seed: int,
             exhaustiveness: int, num_modes: int, out_dir: Path,
             timeout_s: int) -> DockResult: ...

    def rescore(self, poses_sdf: Path, receptor) -> list[float]: ...



class VinaEngine:
    """AutoDock Vina adapter. Always single-threaded (ADR-012).

    INPUTS:   Ligand PDBQT, PreparedReceptor, Box, seed, exhaustiveness.
    OUTPUTS:  DockResult.
    ACCEPTS:  tests/test_engines.py -- same seed gives byte-identical scores; --cpu is always 1.
    EFFORT:   ~1 day.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError(
            "VinaEngine is not implemented; see the class docstring for its contract."
        )


class SminaEngine:
    """smina adapter; the default rescorer via --scoring vinardo.

    INPUTS:   As VinaEngine, plus a scoring-function name.
    OUTPUTS:  DockResult.
    ACCEPTS:  tests/test_engines.py -- vinardo scores differ from vina scores on the same pose.
    EFFORT:   ~0.5 day.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError(
            "SminaEngine is not implemented; see the class docstring for its contract."
        )


class GninaEngine:
    """GNINA adapter. FEATURE-FLAGGED OFF -- no distribution channel here (ADR-005).

    INPUTS:   As VinaEngine.
    OUTPUTS:  DockResult.
    ACCEPTS:  tests/test_engines.py -- instantiating without the feature flag raises a clear error
               naming ADR-005 rather than failing obscurely at subprocess launch.
    EFFORT:   ~1 day once a binary exists. BLOCKED: github 403, absent from conda-forge.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError(
            "GninaEngine is not implemented; see the class docstring for its contract."
        )
