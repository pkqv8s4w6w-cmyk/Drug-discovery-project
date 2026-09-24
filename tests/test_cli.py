"""CLI surface. The dry run must walk the whole graph and stop in one predictable place."""

from __future__ import annotations

import pytest

typer_testing = pytest.importorskip("typer.testing")

from veridian.cli import STAGES, app  # noqa: E402

runner = typer_testing.CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "veridian" in result.stdout


def test_config_show():
    result = runner.invoke(app, ["config", "show", "--tier", "smoke"])
    assert result.exit_code == 0
    assert "tier" in result.stdout


def test_config_show_rejects_a_bad_tier():
    assert runner.invoke(app, ["config", "show", "--tier", "nope"]).exit_code == 1


def test_config_receptors_lists_the_panel():
    result = runner.invoke(app, ["config", "receptors"])
    assert result.exit_code == 0
    assert "6WHA" in result.stdout
    assert "16 structures" in result.stdout


def test_stages_command():
    result = runner.invoke(app, ["stages"])
    assert result.exit_code == 0
    assert "differential" in result.stdout


def test_dry_run_walks_every_stage():
    result = runner.invoke(app, ["smoke", "--dry-run"])
    assert result.exit_code == 0
    assert "dry run complete" in result.stdout


def test_real_run_stops_at_the_first_stub():
    """Exactly one predictable failure point is the intended behaviour of the skeleton."""
    result = runner.invoke(app, ["smoke"])
    assert result.exit_code == 2


def test_validation_precedes_enumeration_in_the_stage_graph():
    """ADR-001: the gate runs before any library is built."""
    names = [s.name for s in STAGES]
    assert names.index("gate") < names.index("enumerate")
    assert names.index("redock") < names.index("gate")
