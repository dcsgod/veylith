"""Veylith command-line interface."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Annotated, Any

import typer

from veylith import __version__
from veylith.errors import (
    AuthorizationMissingError,
    GateFailedError,
    IntegrityVerificationError,
    OperationCancelledError,
    RequiredProviderUnavailableError,
    SandboxUnavailableOrUnsafeError,
    SecurityViolationError,
    UnsupportedArtifactError,
    UsageError,
    VeylithError,
)
from veylith.exitcodes import (
    EXIT_AUTHORIZATION_MISSING,
    EXIT_CANCELLED,
    EXIT_GATE_FAILED,
    EXIT_GENERIC_FAILURE,
    EXIT_INTEGRITY_FAILED,
    EXIT_REQUIRED_PROVIDER_UNAVAILABLE,
    EXIT_SANDBOX_UNAVAILABLE_OR_UNSAFE,
    EXIT_UNSUPPORTED_ARTIFACT,
    EXIT_USAGE_ERROR,
)
from veylith.intake.auth import record_owner_declaration, verify_owner_authorization
from veylith.intake.scanner import ProjectScanner
from veylith.integrity.hasher import sha256_file
from veylith.models.profile import ProtectionProfile
from veylith.protection.engine import ProtectionEngine
from veylith.safety.redaction import redact_secrets

app = typer.Typer(
    name="veylith",
    help="Software protection, exposure measurement, and reconstruction-resistance evaluation.",
    no_args_is_help=True,
)


def _handle_error(err: Exception) -> None:
    msg = redact_secrets(str(err))
    if isinstance(err, AuthorizationMissingError):
        typer.secho(f"Error (Authorization): {msg}", fg=typer.colors.RED, err=True)
        sys.exit(EXIT_AUTHORIZATION_MISSING)
    elif isinstance(err, IntegrityVerificationError):
        typer.secho(f"Error (Integrity): {msg}", fg=typer.colors.RED, err=True)
        sys.exit(EXIT_INTEGRITY_FAILED)
    elif isinstance(err, UnsupportedArtifactError):
        typer.secho(f"Error (Unsupported Artifact): {msg}", fg=typer.colors.RED, err=True)
        sys.exit(EXIT_UNSUPPORTED_ARTIFACT)
    elif isinstance(err, RequiredProviderUnavailableError):
        typer.secho(f"Error (Provider Unavailable): {msg}", fg=typer.colors.RED, err=True)
        sys.exit(EXIT_REQUIRED_PROVIDER_UNAVAILABLE)
    elif isinstance(err, GateFailedError):
        typer.secho(f"Error (Gate Failed): {msg}", fg=typer.colors.RED, err=True)
        sys.exit(EXIT_GATE_FAILED)
    elif isinstance(err, SandboxUnavailableOrUnsafeError):
        typer.secho(f"Error (Sandbox Unsafe): {msg}", fg=typer.colors.RED, err=True)
        sys.exit(EXIT_SANDBOX_UNAVAILABLE_OR_UNSAFE)
    elif isinstance(err, (SecurityViolationError, UsageError)):
        typer.secho(f"Error (Usage/Security): {msg}", fg=typer.colors.RED, err=True)
        sys.exit(EXIT_USAGE_ERROR)
    elif isinstance(err, OperationCancelledError):
        typer.secho("Operation cancelled.", fg=typer.colors.YELLOW, err=True)
        sys.exit(EXIT_CANCELLED)
    elif isinstance(err, VeylithError):
        typer.secho(f"Error: {msg}", fg=typer.colors.RED, err=True)
        sys.exit(err.exit_code)
    else:
        typer.secho(f"Unexpected error: {msg}", fg=typer.colors.RED, err=True)
        sys.exit(EXIT_GENERIC_FAILURE)


@app.command()
def version(
    json_output: Annotated[bool, typer.Option("--json", help="Output version as JSON")] = False,
) -> None:
    """Show the Veylith version and build information."""
    data = {
        "name": "veylith",
        "version": __version__,
        "schema_version": "0.1.0",
        "python_version": sys.version.split()[0],
    }
    if json_output:
        typer.echo(json.dumps(data, indent=2))
    else:
        typer.echo(f"Veylith version {__version__} (Python {sys.version.split()[0]})")


@app.command()
def doctor(
    json_output: Annotated[
        bool, typer.Option("--json", help="Output doctor diagnostics as JSON")
    ] = False,
) -> None:
    """Inspect environment diagnostics, toolchains, and sandbox availability."""
    node_path = shutil.which("node")
    podman_path = shutil.which("podman")
    docker_path = shutil.which("docker")
    git_path = shutil.which("git")

    py_ver = sys.version.split()[0]
    node_status = "available" if node_path else "unavailable (JS advanced bundling disabled)"
    sandbox_status = (
        "ready" if (podman_path or docker_path) else "unavailable (dynamic tests disabled)"
    )

    diagnostics: dict[str, Any] = {
        "veylith_version": __version__,
        "python": {"version": py_ver, "status": "ok"},
        "git": {"available": bool(git_path), "path": git_path},
        "node": {
            "available": bool(node_path),
            "path": node_path,
            "status": node_status,
        },
        "sandbox": {
            "podman": bool(podman_path),
            "docker": bool(docker_path),
            "status": sandbox_status,
        },
    }

    if json_output:
        typer.echo(json.dumps(diagnostics, indent=2))
    else:
        typer.secho("=== Veylith Environment Diagnostics ===", bold=True)
        typer.echo(f"  Python:  {py_ver} (OK)")
        typer.echo(f"  Git:     {'Found' if git_path else 'Missing'}")
        typer.echo(f"  Node.js: {node_status}")
        typer.echo(f"  Sandbox: {sandbox_status}")


@app.command()
def init(
    project_path: Annotated[
        Path, typer.Argument(help="Path to the software project to initialize")
    ],
    declared_by: Annotated[
        str, typer.Option("--declared-by", help="Owner identifier")
    ] = "operator",
    scope: Annotated[
        str, typer.Option("--scope", help="Authorization scope")
    ] = "authorized-security-evaluation",
    json_output: Annotated[bool, typer.Option("--json", help="Output JSON confirmation")] = False,
) -> None:
    """Record an owner authorization declaration for a software project."""
    try:
        resolved_path = project_path.resolve()
        if not resolved_path.exists() or not resolved_path.is_dir():
            raise UsageError(f"Target directory does not exist: {project_path}")

        declaration = record_owner_declaration(resolved_path, declared_by=declared_by, scope=scope)
        if json_output:
            typer.echo(declaration.model_dump_json(indent=2))
        else:
            typer.secho(
                f"[OK] Owner declaration recorded for '{resolved_path.name}'. "
                f"Declared by: {declared_by} (Scope: {scope})",
                fg=typer.colors.GREEN,
            )
    except Exception as err:
        _handle_error(err)


@app.command()
def inspect(
    artifact_path: Annotated[Path, typer.Argument(help="Path to project or artifact to inspect")],
    json_output: Annotated[bool, typer.Option("--json", help="Output results in JSON")] = False,
) -> None:
    """Inspect an authorized project or artifact structure without modification."""
    try:
        resolved = artifact_path.resolve()
        verify_owner_authorization(resolved)
        scanner = ProjectScanner(resolved)
        manifest = scanner.scan()

        data = {
            "root": manifest.root,
            "manifest_digest": manifest.manifest_digest,
            "total_files": manifest.total_files,
            "total_bytes": manifest.total_bytes,
        }
        if json_output:
            typer.echo(json.dumps(data, indent=2))
        else:
            typer.secho(f"=== Project Inspection: {resolved.name} ===", bold=True)
            typer.echo(f"  Files:  {manifest.total_files}")
            typer.echo(f"  Bytes:  {manifest.total_bytes}")
            typer.echo(f"  Digest: {manifest.manifest_digest}")
    except Exception as err:
        _handle_error(err)


@app.command()
def inventory(
    artifact_path: Annotated[Path, typer.Argument(help="Path to project to inventory")],
    json_output: Annotated[bool, typer.Option("--json", help="Output manifest JSON")] = False,
) -> None:
    """Generate a canonical file inventory and SHA-256 manifest of an authorized project."""
    try:
        resolved = artifact_path.resolve()
        verify_owner_authorization(resolved)
        scanner = ProjectScanner(resolved)
        manifest = scanner.scan()

        if json_output:
            typer.echo(manifest.model_dump_json(indent=2))
        else:
            typer.secho(f"=== Inventory: {manifest.total_files} files ===", bold=True)
            for f in manifest.files:
                typer.echo(f"  {f.path:<40} {f.sha256[:16]}... ({f.size_bytes} B)")
            typer.echo(f"Canonical Manifest Digest: {manifest.manifest_digest}")
    except Exception as err:
        _handle_error(err)


@app.command()
def protect(
    project_path: Annotated[Path, typer.Argument(help="Authorized project root")],
    out: Annotated[Path, typer.Option("--out", help="Output directory for protected artifact")],
    profile_name: Annotated[
        str, typer.Option("--profile", help="Protection profile name")
    ] = "default",
    json_output: Annotated[bool, typer.Option("--json", help="Output report JSON")] = False,
) -> None:
    """Apply configured protection pipeline into an isolated output directory."""
    try:
        resolved_in = project_path.resolve()
        verify_owner_authorization(resolved_in)

        resolved_out = out.resolve()
        profile = ProtectionProfile(name=profile_name)

        engine = ProtectionEngine(target_root=resolved_in, output_dir=resolved_out, profile=profile)
        report, protected_manifest = engine.run()

        # Save report and manifest into output directory
        report_file = resolved_out / "veylith_report.json"
        manifest_file = resolved_out / "veylith_manifest.json"
        report_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        manifest_file.write_text(protected_manifest.model_dump_json(indent=2), encoding="utf-8")

        if json_output:
            typer.echo(report.model_dump_json(indent=2))
        else:
            typer.secho(
                f"[OK] Protection applied successfully to '{resolved_out}'", fg=typer.colors.GREEN
            )
            typer.echo(f"  Original Digest:  {report.target_digest}")
            typer.echo(f"  Protected Digest: {report.protected_digest}")
            for control in report.controls:
                color = typer.colors.GREEN if control.status == "verified" else typer.colors.YELLOW
                typer.secho(
                    f"  [{control.status.upper()}] {control.name}: {control.details}", fg=color
                )
    except Exception as err:
        _handle_error(err)


@app.command()
def verify(
    protected_artifact: Annotated[
        Path, typer.Argument(help="Protected artifact directory to verify")
    ],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output verification as JSON")
    ] = False,
) -> None:
    """Verify integrity of a protected artifact directory against its recorded manifest."""
    try:
        resolved = protected_artifact.resolve()
        manifest_path = resolved / "veylith_manifest.json"
        if not manifest_path.is_file():
            raise IntegrityVerificationError(f"Missing veylith_manifest.json in '{resolved}'")

        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest_dict = json.load(f)
        except Exception as err:
            raise IntegrityVerificationError(f"Malformed manifest JSON: {err}") from err

        files = manifest_dict.get("files", [])
        mismatches: list[str] = []

        for record in files:
            path_str = record.get("path")
            expected_digest = record.get("sha256")
            if not path_str or not expected_digest:
                continue

            file_on_disk = resolved / path_str
            if not file_on_disk.is_file():
                mismatches.append(f"Missing file: {path_str}")
                continue

            actual_digest = sha256_file(file_on_disk)
            if actual_digest != expected_digest:
                mismatches.append(
                    f"Digest mismatch in '{path_str}': "
                    f"expected {expected_digest}, got {actual_digest}"
                )

        if mismatches:
            raise IntegrityVerificationError(f"Integrity check failed: {'; '.join(mismatches)}")

        result = {
            "status": "verified",
            "files_checked": len(files),
            "manifest_digest": manifest_dict.get("manifest_digest"),
        }
        if json_output:
            typer.echo(json.dumps(result, indent=2))
        else:
            typer.secho(
                f"[OK] Protected artifact verified ({len(files)} files checked).",
                fg=typer.colors.GREEN,
            )
    except Exception as err:
        _handle_error(err)


@app.command()
def report(
    report_file: Annotated[Path, typer.Argument(help="Path to veylith_report.json")],
    format: Annotated[str, typer.Option("--format", help="Output format: json, md")] = "json",
) -> None:
    """Display or format a saved protection report."""
    try:
        resolved = report_file.resolve()
        if not resolved.is_file():
            raise UsageError(f"Report file not found: {report_file}")

        with open(resolved, encoding="utf-8") as f:
            data = json.load(f)

        if format == "json":
            typer.echo(json.dumps(data, indent=2))
        elif format == "md":
            typer.echo(f"# Veylith Protection Report ({data.get('run_id')})\n")
            typer.echo(f"- **Target Digest:** `{data.get('target_digest')}`")
            typer.echo(f"- **Protected Digest:** `{data.get('protected_digest')}`\n")
            typer.echo("## Controls")
            for c in data.get("controls", []):
                typer.echo(f"- **{c.get('name')}:** `{c.get('status')}` ({c.get('details')})")
            typer.echo("\n## What This Report Does Not Show")
            for caveat in data.get("not_shown_caveats", []):
                typer.echo(f"- {caveat}")
        else:
            raise UsageError(f"Unsupported report format: {format}")
    except Exception as err:
        _handle_error(err)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
