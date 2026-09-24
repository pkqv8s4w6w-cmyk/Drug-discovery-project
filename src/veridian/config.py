"""Layered YAML configuration with validation.

Config resolution order, later overriding earlier:

    configs/base.yaml  ->  configs/tiers/<tier>.yaml  ->  CLI overrides

Every path in the pipeline derives from a resolved config. No module hardcodes a path,
and no module reads a YAML file directly -- that keeps `veridian config show` an honest
representation of what a run will actually do.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "configs"

Tier = Literal["smoke", "gate", "dev", "full"]
VALID_TIERS: tuple[str, ...] = ("smoke", "gate", "dev", "full")


class ConfigError(ValueError):
    """Raised when a configuration is missing, malformed, or internally inconsistent."""


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge `override` into `base`, returning a new dict.

    Mappings merge key-wise; every other type (including lists) replaces wholesale.
    Lists replace rather than concatenate so that a tier can shorten a receptor panel.
    """
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"config file not found: {path}")
    with path.open() as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"config file must contain a mapping at top level: {path}")
    return data


@dataclass(frozen=True)
class Config:
    """A fully resolved run configuration."""

    tier: str
    data: dict[str, Any] = field(repr=False)

    def get(self, dotted: str, default: Any = None) -> Any:
        """Fetch a nested value by dotted path, e.g. `config.get("compute.n_workers")`."""
        node: Any = self.data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def require(self, dotted: str) -> Any:
        """Like `get`, but raises `ConfigError` when the key is absent."""
        sentinel = object()
        value = self.get(dotted, sentinel)
        if value is sentinel:
            raise ConfigError(f"required config key missing: {dotted}")
        return value

    def canonical_json(self) -> str:
        """Stable JSON used for run-id hashing. Key order is deterministic."""
        return json.dumps(self.data, sort_keys=True, separators=(",", ":"))

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()

    def dump(self) -> str:
        return yaml.safe_dump(self.data, sort_keys=True, default_flow_style=False)


def load_config(
    tier: str = "smoke",
    overrides: dict[str, Any] | None = None,
    config_dir: Path | None = None,
) -> Config:
    """Resolve base + tier + overrides into a validated `Config`.

    Args:
        tier: one of `VALID_TIERS`.
        overrides: nested dict merged last, typically from CLI flags.
        config_dir: defaults to `configs/`; injectable for tests.

    Raises:
        ConfigError: unknown tier, missing file, or failed validation.
    """
    if tier not in VALID_TIERS:
        raise ConfigError(f"unknown tier {tier!r}; expected one of {VALID_TIERS}")

    cfg_dir = config_dir or CONFIG_DIR
    merged = _read_yaml(cfg_dir / "base.yaml")
    merged = _deep_merge(merged, _read_yaml(cfg_dir / "tiers" / f"{tier}.yaml"))
    if overrides:
        merged = _deep_merge(merged, overrides)
    merged.setdefault("tier", tier)

    config = Config(tier=tier, data=merged)
    validate(config)
    return config


def validate(config: Config) -> None:
    """Check cross-field invariants that a schema alone would not catch.

    Raises:
        ConfigError: on any violation.
    """
    if config.get("seed") is None:
        raise ConfigError("`seed` is required -- runs must be reproducible")

    workers = config.get("compute.n_workers", 1)
    if not isinstance(workers, int) or workers < 1:
        raise ConfigError(f"compute.n_workers must be a positive int, got {workers!r}")

    # ADR-012: Vina is only reproducible single-threaded. Guard it in config, not in a comment.
    vina_cpu = config.get("compute.vina_cpu_per_process", 1)
    if vina_cpu != 1:
        raise ConfigError(
            "compute.vina_cpu_per_process must be 1: Vina is non-deterministic with "
            "--cpu > 1 even at a fixed seed, which breaks test_determinism. "
            "Parallelise with more processes instead (ADR-012)."
        )

    dispatch = config.get("compute.dispatch", "local")
    if dispatch not in {"local", "slurm", "awsbatch"}:
        raise ConfigError(f"unknown compute.dispatch: {dispatch!r}")

    budget = config.get("screen.n_dock_budget", 0)
    if not isinstance(budget, int) or budget < 0:
        raise ConfigError(f"screen.n_dock_budget must be a non-negative int, got {budget!r}")

    # ADR-010: enumeration and docking are separate budgets. Catch the conflation early,
    # because docking a whole 1M-compound library is ~87 days on this hardware.
    n_target = config.get("library.n_target", 0)
    if isinstance(n_target, int) and n_target > 0 and budget > n_target:
        raise ConfigError(
            f"screen.n_dock_budget ({budget}) exceeds library.n_target ({n_target}); "
            "the dock budget is a subset of the enumerated library (ADR-010)"
        )


def load_receptors(config_dir: Path | None = None) -> dict[str, Any]:
    """Load the receptor panel, including the Ballesteros-Weinstein maps.

    Kept separate from `load_config` because the panel is shared across tiers and is
    large enough that inlining it would drown the resolved config.
    """
    return _read_yaml((config_dir or CONFIG_DIR) / "receptors.yaml")
