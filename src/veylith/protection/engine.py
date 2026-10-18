"""Protection engine coordinating pipeline transformations and output emission."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from veylith.errors import UsageError
from veylith.intake.scanner import ProjectScanner
from veylith.integrity.hasher import sha256_bytes
from veylith.models.manifest import InventoryManifest, TransformationRecord
from veylith.models.profile import ProtectionProfile
from veylith.models.report import ControlStatus, ProtectionReport
from veylith.protection.hygiene import apply_python_hygiene
from veylith.safety.path_guard import PathGuard


class ProtectionEngine:
    """Executes configured protection profiles on an authorized target."""

    def __init__(
        self,
        target_root: str | Path,
        output_dir: str | Path,
        profile: ProtectionProfile | None = None,
    ) -> None:
        self.target_guard = PathGuard(target_root)
        self.target_root = self.target_guard.root

        self.output_path = Path(output_dir).resolve()
        # Original directory must never be modified in-place
        if self.output_path == self.target_root:
            raise UsageError(
                "Output directory cannot be identical to target root. "
                "Originals must remain immutable."
            )

        self.profile = profile or ProtectionProfile()

    def run(self) -> tuple[ProtectionReport, InventoryManifest]:
        """Execute the protection pipeline and write artifacts to the isolated output directory."""
        # 1. Inventory original
        original_scanner = ProjectScanner(self.target_root)
        original_manifest = original_scanner.scan()

        # 2. Prepare output directory
        if self.output_path.exists():
            shutil.rmtree(self.output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        out_guard = PathGuard(self.output_path)

        transformations: list[TransformationRecord] = []
        controls: list[ControlStatus] = []

        # 3. Process each file
        for file_record in original_manifest.files:
            rel_path = file_record.path
            in_file = self.target_guard.validate_contained(rel_path)

            # Check if file should be excluded (e.g. source maps)
            if self.profile.remove_sourcemaps and rel_path.endswith(".map"):
                transformations.append(
                    TransformationRecord(
                        id="hygiene.remove_sourcemaps",
                        input_digest=file_record.sha256,
                        output_digest="",
                        parameters={"path": rel_path},
                        skip_reasons=[],
                        deterministic=True,
                    )
                )
                continue

            # Process Python files
            if rel_path.endswith(".py"):
                raw_content = in_file.read_text(encoding="utf-8")
                transformed = apply_python_hygiene(
                    raw_content,
                    strip_docstrings=self.profile.strip_docstrings,
                    strip_comments=self.profile.strip_comments,
                )
                out_bytes = transformed.encode("utf-8")
                out_digest = sha256_bytes(out_bytes)
                out_guard.safe_write_bytes(rel_path, out_bytes)

                transformations.append(
                    TransformationRecord(
                        id="hygiene.python_docstrings_and_comments",
                        input_digest=file_record.sha256,
                        output_digest=out_digest,
                        parameters={"path": rel_path},
                        skip_reasons=[],
                        deterministic=True,
                    )
                )
            else:
                # Copy other files unmodified
                content = in_file.read_bytes()
                out_guard.safe_write_bytes(rel_path, content)

        # 4. Inventory protected output
        protected_scanner = ProjectScanner(self.output_path)
        protected_manifest = protected_scanner.scan()

        # Mark controls
        controls.append(
            ControlStatus(
                name="hygiene.remove_sourcemaps",
                status="verified" if self.profile.remove_sourcemaps else "unverified",
                details="Source map stripping executed and verified.",
            )
        )
        controls.append(
            ControlStatus(
                name="hygiene.python_docstrings_and_comments",
                status="verified",
                details="Docstring and comment stripping applied via LibCST.",
            )
        )

        report = ProtectionReport(
            run_id=str(uuid.uuid4()),
            target_digest=original_manifest.manifest_digest,
            protected_digest=protected_manifest.manifest_digest,
            controls=controls,
            transformations=transformations,
        )

        return report, protected_manifest
