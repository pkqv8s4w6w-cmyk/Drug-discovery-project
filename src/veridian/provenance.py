"""Run provenance: what ran, from what code, against what inputs.

The reproducibility spine. Every stage writes into a single per-run manifest so that a
candidate list can be traced back to the exact config, code revision, input files and
binary versions that produced it.

One rule matters more than the rest: the manifest records the SHA-256 of
`PREREGISTRATION.md`. If that file changed between the gate run and a screening run, the
report says so in its header. A pre-registration that can be quietly edited afterwards is
not a pre-registration.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from veridian.config import REPO_ROOT, Config


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Stream a file through SHA-256. Handles multi-GB parquet without loading it."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(cmd: list[str]) -> str | None:
    """Best-effort capture of a subprocess's stdout. Returns None on any failure."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def git_revision() -> dict[str, Any]:
    """Current commit, branch, and whether the tree is dirty."""
    sha = _run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"])
    branch = _run(["git", "-C", str(REPO_ROOT), "rev-parse", "--abbrev-ref", "HEAD"])
    status = _run(["git", "-C", str(REPO_ROOT), "status", "--porcelain"])
    return {"sha": sha, "branch": branch, "dirty": bool(status)}


def binary_versions() -> dict[str, str | None]:
    """Versions of the external docking binaries, recorded because scores depend on them."""
    return {
        "vina": _run(["vina", "--version"]),
        "smina": _run(["smina", "--version"]),
        "obabel": _run(["obabel", "-V"]),
    }


def preregistration_hash() -> str | None:
    """SHA-256 of PREREGISTRATION.md, or None if it is missing (which is itself a finding)."""
    path = REPO_ROOT / "PREREGISTRATION.md"
    return sha256_file(path) if path.is_file() else None


def compute_run_id(config: Config) -> str:
    """Deterministic 12-char run id from config + code revision + environment.

    Two runs sharing a run_id should produce identical output; if they do not, something
    outside this hash is leaking in, which is worth knowing.
    """
    parts = [
        config.canonical_json(),
        git_revision().get("sha") or "nogit",
        _run(["python", "-m", "pip", "freeze"]) or "nofreeze",
    ]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:12]


@dataclass
class RunManifest:
    """Accumulates provenance across stages, then writes it once.

    Usage:
        manifest = RunManifest.start(config)
        with manifest.stage("dock"):
            ...
        manifest.record_output(path)
        manifest.write()
    """

    run_id: str
    config: Config
    started_at: str
    git: dict[str, Any]
    environment: dict[str, Any]
    binaries: dict[str, str | None]
    preregistration_sha256: str | None
    stages: list[dict[str, Any]] = field(default_factory=list)
    inputs: dict[str, str] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)

    @classmethod
    def start(cls, config: Config) -> RunManifest:
        return cls(
            run_id=compute_run_id(config),
            config=config,
            started_at=datetime.now(UTC).isoformat(),
            git=git_revision(),
            environment={
                "python": platform.python_version(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "hostname": platform.node(),
            },
            binaries=binary_versions(),
            preregistration_sha256=preregistration_hash(),
        )

    @property
    def run_dir(self) -> Path:
        return REPO_ROOT / self.config.get("paths.runs", "runs") / self.run_id

    def record_input(self, path: Path) -> None:
        if path.is_file():
            self.inputs[str(path.relative_to(REPO_ROOT))] = sha256_file(path)

    def record_output(self, path: Path) -> None:
        if path.is_file():
            self.outputs[str(path.relative_to(REPO_ROOT))] = sha256_file(path)

    def stage(self, name: str) -> _StageTimer:
        """Context manager recording wall and CPU time for one stage."""
        return _StageTimer(self, name)

    def write(self) -> Path:
        """Write manifest.json and the config snapshot. Returns the manifest path."""
        self.run_dir.mkdir(parents=True, exist_ok=True)
        (self.run_dir / "config.snapshot.yaml").write_text(self.config.dump())
        payload = {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": datetime.now(UTC).isoformat(),
            "tier": self.config.tier,
            "config_sha256": self.config.sha256(),
            "preregistration_sha256": self.preregistration_sha256,
            "git": self.git,
            "environment": self.environment,
            "binaries": self.binaries,
            "stages": self.stages,
            "inputs": self.inputs,
            "outputs": self.outputs,
        }
        path = self.run_dir / "manifest.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))
        return path


class _StageTimer:
    def __init__(self, manifest: RunManifest, name: str) -> None:
        self._manifest = manifest
        self._name = name
        self._wall = 0.0
        self._cpu = 0.0

    def __enter__(self) -> _StageTimer:
        self._wall = time.perf_counter()
        self._cpu = time.process_time()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self._manifest.stages.append(
            {
                "name": self._name,
                "wall_seconds": round(time.perf_counter() - self._wall, 3),
                "cpu_seconds": round(time.process_time() - self._cpu, 3),
                "failed": exc_type is not None,
            }
        )


def check_preregistration_drift(recorded: str | None) -> str | None:
    """Compare a recorded pre-registration hash against the file on disk now.

    Returns:
        None when the hashes agree (or there is nothing to compare), otherwise a
        human-readable warning for the report header.
    """
    current = preregistration_hash()
    if recorded is None or current is None or recorded == current:
        return None
    return (
        "PREREGISTRATION.md has changed since this run's criteria were fixed "
        f"(recorded {recorded[:12]}, current {current[:12]}). Any gate result below was "
        "evaluated against different criteria than those now on disk."
    )
