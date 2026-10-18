"""Integration tests for CLI commands and stable exit codes."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from veylith.cli import app
from veylith.exitcodes import (
    EXIT_AUTHORIZATION_MISSING,
    EXIT_OK,
)

runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == EXIT_OK
    assert "Veylith version 0.1.0" in result.stdout


def test_cli_version_json() -> None:
    result = runner.invoke(app, ["version", "--json"])
    assert result.exit_code == EXIT_OK
    assert '"name": "veylith"' in result.stdout


def test_cli_doctor() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == EXIT_OK
    assert "Veylith Environment Diagnostics" in result.stdout


def test_cli_inspect_without_auth_fails_exit_3(tmp_path: Path) -> None:
    # Target directory without .veylith.yaml
    result = runner.invoke(app, ["inspect", str(tmp_path)])
    assert result.exit_code == EXIT_AUTHORIZATION_MISSING
    assert (
        "No owner authorization declaration found" in result.stderr
        or "No owner authorization declaration found" in result.stdout
    )


def test_cli_init_records_auth_and_inspect_succeeds(tmp_path: Path) -> None:
    sample_file = tmp_path / "app.py"
    sample_file.write_text("print('hello')", encoding="utf-8")

    # Run veylith init
    init_res = runner.invoke(app, ["init", str(tmp_path), "--declared-by", "alice"])
    assert init_res.exit_code == EXIT_OK
    assert (tmp_path / ".veylith.yaml").exists()

    # Now inspect succeeds
    inspect_res = runner.invoke(app, ["inspect", str(tmp_path)])
    assert inspect_res.exit_code == EXIT_OK
    assert "Project Inspection" in inspect_res.stdout
