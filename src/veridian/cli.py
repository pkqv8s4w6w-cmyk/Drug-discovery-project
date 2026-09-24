"""VERIDIAN command line interface.

    veridian --help
    veridian config show --tier smoke
    veridian smoke --dry-run

`--dry-run` walks the full stage graph without computing and reports which stages are
implemented and which are still stubs. In the current skeleton that walk is the point: it
should traverse the entire pipeline and stop at the first unimplemented stage, naming the
stub and its contract.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass

import typer

from veridian import __version__
from veridian.config import ConfigError, load_config, load_receptors

app = typer.Typer(
    name="veridian",
    help="Structure-based discovery of non-hallucinogenic 5-HT2A agonists.",
    add_completion=False,
    no_args_is_help=True,
)
config_app = typer.Typer(help="Inspect resolved configuration.", no_args_is_help=True)
app.add_typer(config_app, name="config")


@dataclass(frozen=True)
class Stage:
    """One pipeline stage and whether it currently computes anything."""

    name: str
    step: str
    description: str
    implemented: bool
    entrypoint: str


# The pipeline in execution order. Validation sits at the gate, before enumeration (ADR-001).
STAGES: tuple[Stage, ...] = (
    Stage("reference", "1", "Load and validate the reference set",
          True, "veridian.data.reference:load_reference_set"),
    Stage("fetch-structures", "2", "Download the receptor panel from RCSB",
          False, "veridian.structure.fetch:fetch_structure"),
    Stage("prepare-receptors", "2", "Clean, protonate and convert to PDBQT",
          False, "veridian.structure.prepare:prepare_receptor"),
    Stage("redock", "7a", "Redock native ligands; symmetry-corrected RMSD gate",
          False, "veridian.structure.redock:redock_native"),
    Stage("fetch-chembl", "5a", "Pull and curate bioactivity data",
          False, "veridian.data.chembl:fetch_activities"),
    Stage("decoys", "7b", "Build verified-inactive and property-matched decoy sets",
          False, "veridian.data.decoys:build_decoy_sets"),
    Stage("background", "6a", "Dock the shared decoy background into every receptor",
          False, "veridian.dock.normalize:fit_background"),
    Stage("gate", "7c", "Evaluate the seven pre-registered criteria",
          False, "veridian.eval.report:evaluate_gate"),
    Stage("enumerate", "3", "Enumerate the bespoke library",
          False, "veridian.library.enumerate:enumerate_library"),
    Stage("dock", "4", "Docking cascade over the library",
          False, "veridian.dock.runner:dock_library"),
    Stage("rescore", "4b", "Vinardo + interaction-fingerprint rescoring",
          False, "veridian.dock.rescore:rescore_poses"),
    Stage("models", "5b", "Train 2A affinity, 2A Emax, 2B agonism, HTR",
          False, "veridian.ml.regressors:train_all"),
    Stage("differential", "6", "Delta-z across pocket families + permutation null",
          False, "veridian.screen.differential:differential_scores"),
    Stage("select", "8", "Cluster, rank and render the candidate report",
          False, "veridian.screen.select:select_candidates"),
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"veridian {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """Structure-based discovery of non-hallucinogenic 5-HT2A agonists."""


@config_app.command("show")
def config_show(
    tier: str = typer.Option("smoke", "--tier", "-t", help="smoke | gate | dev | full"),
) -> None:
    """Resolve base + tier and print the validated configuration."""
    try:
        config = load_config(tier)
    except ConfigError as exc:
        typer.secho(f"config error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc
    typer.echo(f"# tier: {config.tier}   sha256: {config.sha256()[:12]}")
    typer.echo(config.dump())


@config_app.command("receptors")
def config_receptors() -> None:
    """Summarise the receptor panel and its differential families."""
    panel = load_receptors()
    families = panel.get("families", {})
    receptors = panel.get("receptors", {})
    for family, members in families.items():
        typer.secho(f"\n{family}", fg=typer.colors.CYAN, bold=True)
        for pdb_id in members:
            entry = receptors.get(pdb_id, {})
            ligand = entry.get("native_ligand", "-")
            typer.echo(
                f"  {pdb_id}  {entry.get('resolution', '?'):>5} A  "
                f"{entry.get('method', '?'):<8} {ligand}"
            )
    typer.echo(f"\n{len(receptors)} structures total.")


def _walk(tier: str, dry_run: bool) -> int:
    """Walk the stage graph. Returns a process exit code."""
    try:
        config = load_config(tier)
    except ConfigError as exc:
        typer.secho(f"config error: {exc}", fg=typer.colors.RED, err=True)
        return 1

    typer.secho(f"VERIDIAN {tier} run", fg=typer.colors.CYAN, bold=True)
    typer.echo(f"config sha256 : {config.sha256()[:12]}")
    typer.echo(f"dock budget   : {config.get('screen.n_dock_budget', 0):,} ligands")
    typer.echo(f"library target: {config.get('library.n_target', 0):,} compounds")
    typer.echo(f"workers       : {config.get('compute.n_workers', 1)}\n")

    for stage in STAGES:
        mark = "ok  " if stage.implemented else "STUB"
        colour = typer.colors.GREEN if stage.implemented else typer.colors.YELLOW
        typer.secho(f"  [{mark}] step {stage.step:<3} {stage.name:<20} {stage.description}",
                    fg=colour)
        if not stage.implemented and not dry_run:
            typer.secho(
                f"\nStage {stage.name!r} is not implemented.\n"
                f"  entrypoint: {stage.entrypoint}\n"
                f"  Read its docstring for the input/output/acceptance/effort contract.\n"
                f"  Re-run with --dry-run to walk the remaining stages.",
                fg=typer.colors.RED, err=True,
            )
            return 2

    if dry_run:
        done = sum(1 for s in STAGES if s.implemented)
        typer.secho(f"\ndry run complete: {done}/{len(STAGES)} stages implemented.",
                    fg=typer.colors.CYAN)
    return 0


def _tier_command(tier: str, help_text: str) -> Callable[[bool], None]:
    def command(
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Walk the stage graph without computing.",
        ),
    ) -> None:
        raise typer.Exit(_walk(tier, dry_run))

    command.__doc__ = help_text
    return command


app.command("smoke")(_tier_command("smoke", "Smoke tier: ~60 ligands, one receptor, ~7.5 min."))
app.command("gate")(_tier_command("gate", "Gate tier: the pre-registered go/no-go, ~24 h."))
app.command("dev")(_tier_command("dev", "Dev tier: ~2,000 ligands overnight."))
app.command("full")(_tier_command("full", "Full tier: not runnable here; emits a job spec."))


@app.command("stages")
def stages() -> None:
    """List every pipeline stage and its implementation status."""
    for stage in STAGES:
        mark = "ok" if stage.implemented else "stub"
        typer.echo(f"{mark:<5} step {stage.step:<4} {stage.name:<20} {stage.entrypoint}")


def run() -> None:
    try:
        app()
    except KeyboardInterrupt:
        typer.secho("\ninterrupted", fg=typer.colors.YELLOW, err=True)
        sys.exit(130)


if __name__ == "__main__":
    run()
