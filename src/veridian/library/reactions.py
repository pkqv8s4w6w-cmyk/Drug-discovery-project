"""Reaction SMARTS registry, loaded from configs/reactions/*.yaml.

Day-one routes are Pictet-Spengler (tetrahydro-beta-carboline) and azepinoindole. The
azepinoindole route replaced isoquinuclidine after structure verification showed
tabernanthalog is an azepinoindole, not an isoquinuclidine -- see ADR-004.
"""

from __future__ import annotations

from pathlib import Path


def load_route(name: str, config_dir: Path | None = None) -> dict:
    """Load one reaction route definition.

    INPUTS:   Route name, optional config directory.
    OUTPUTS:  Route dict with compiled reaction SMARTS and building-block role queries.
    ACCEPTS:  tests/test_reactions.py -- every shipped route file loads and its SMARTS compiles.
    EFFORT:   ~2 h for the loader.
    """

    raise NotImplementedError(
        "load_route is not implemented; see the docstring for its contract."
    )


def apply_route(route: dict, reagents: list) -> list:
    """Apply a route to one reagent combination.

    INPUTS:   Route dict, reagent molecules.
    OUTPUTS:  Product molecules, sanitised and canonicalised.
    ACCEPTS:  tests/test_reactions.py -- each route reconstructs its own exemplar: the
               azepinoindole route must regenerate tabernanthalog (FNGNYGCPNKZYOG-UHFFFAOYSA-N). A
               route that cannot rebuild its exemplar is wrong.
    EFFORT:   ~2 days per route. All five currently carry smarts_status: PLACEHOLDER.
    """

    raise NotImplementedError(
        "apply_route is not implemented; see the docstring for its contract."
    )
