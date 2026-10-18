"""End-to-end walking skeleton test for Phase 0."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from veylith.cli import app
from veylith.exitcodes import EXIT_INTEGRITY_FAILED, EXIT_OK
from veylith.integrity.hasher import sha256_file

runner = CliRunner()


def test_walking_skeleton_end_to_end(tmp_path: Path) -> None:
    # 1. Setup sample project
    src_dir = (
        Path(__file__).resolve().parent.parent.parent / "examples" / "sample_apps" / "tiny_calc"
    )
    target_dir = tmp_path / "tiny_calc"
    shutil.copytree(src_dir, target_dir)

    calc_file = target_dir / "calculator.py"
    original_digest = sha256_file(calc_file)

    # 2. Initialize owner authorization
    init_res = runner.invoke(app, ["init", str(target_dir), "--declared-by", "test-operator"])
    assert init_res.exit_code == EXIT_OK

    # 3. Inventory target
    inv_res = runner.invoke(app, ["inventory", str(target_dir), "--json"])
    assert inv_res.exit_code == EXIT_OK
    inv_data = json.loads(inv_res.stdout)
    assert inv_data["total_files"] >= 2
    assert inv_data["manifest_digest"] != ""

    # 4. Protect target into separate output directory
    out_dir = tmp_path / "protected_out"
    prot_res = runner.invoke(app, ["protect", str(target_dir), "--out", str(out_dir), "--json"])
    assert prot_res.exit_code == EXIT_OK

    # 5. IMMUTABILITY CHECK: Original files must be unchanged
    assert sha256_file(calc_file) == original_digest

    # 6. Check protected output has hygiene applied (no docstrings)
    prot_calc = out_dir / "calculator.py"
    assert prot_calc.is_file()
    prot_text = prot_calc.read_text(encoding="utf-8")
    assert "Tiny calculator module for verification testing" not in prot_text
    assert "Calculate the sum of two numbers" not in prot_text

    # 7. BEHAVIORAL EQUIVALENCE: run tests on protected code
    test_run = subprocess.run(
        [sys.executable, "-m", "pytest", str(out_dir / "test_calculator.py")],
        capture_output=True,
        text=True,
        cwd=str(out_dir),
    )
    assert test_run.returncode == 0, (
        f"Protected code failed tests:\n{test_run.stdout}\n{test_run.stderr}"
    )

    # 8. Verify protected artifact integrity
    verify_res = runner.invoke(app, ["verify", str(out_dir)])
    assert verify_res.exit_code == EXIT_OK
    assert "Protected artifact verified" in verify_res.stdout

    # 9. TAMPER CHECK: Modify a single byte in the protected artifact
    prot_calc.write_text(prot_text + "\n# TAMPERED\n", encoding="utf-8")
    tamper_res = runner.invoke(app, ["verify", str(out_dir)])
    assert tamper_res.exit_code == EXIT_INTEGRITY_FAILED

    # 10. Report generation
    report_file = out_dir / "veylith_report.json"
    rep_res = runner.invoke(app, ["report", str(report_file), "--format", "md"])
    assert rep_res.exit_code == EXIT_OK
    assert "# Veylith Protection Report" in rep_res.stdout
    assert "What This Report Does Not Show" in rep_res.stdout
