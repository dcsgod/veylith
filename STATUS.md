# Veylith — Capability & Verification Ledger

Last Updated: Phase 0 (Walking Skeleton Complete)
Claims Policy Rule: Documentation, READMEs, CLI outputs, and reports may ONLY claim capabilities that are marked `implemented` with passing tests linked below. Any control lacking verified passing tests is strictly `unverified`.

## Capability Matrix

| Area | Capability | Status | Test Proof / Link | Verification Date |
|---|---|---|---|---|
| **CLI & Core** | CLI skeleton (`--help`, `--version`, exit codes) | implemented | [test_cli_exitcodes.py](file:///d:/veylith/tests/integration/test_cli_exitcodes.py) | 2026-10-18 |
| | `veylith doctor` environment diagnostics | implemented | [test_cli_doctor](file:///d:/veylith/tests/integration/test_cli_exitcodes.py#L29-L33) | 2026-10-18 |
| | `veylith init` owner authorization declaration | implemented | [test_cli_init](file:///d:/veylith/tests/integration/test_cli_exitcodes.py#L43-L56) | 2026-10-18 |
| | Configuration management & schema validation | partial | [models/base.py](file:///d:/veylith/src/veylith/models/base.py) | 2026-10-18 |
| | SQLite audit storage & schema migrations | not started | - | - |
| | Structured logging with secret redaction | implemented | [test_redaction.py](file:///d:/veylith/tests/unit/test_redaction.py) | 2026-10-18 |
| **Safety & Intake** | Canonical path guard & TOCTOU prevention | implemented | [test_path_guard.py](file:///d:/veylith/tests/unit/test_path_guard.py) | 2026-10-18 |
| | Symlink/junction/zip-slip/zip-bomb protection | partial | [test_path_guard.py](file:///d:/veylith/tests/unit/test_path_guard.py) | 2026-10-18 |
| | SHA-256 deterministic manifest generation | implemented | [test_walking_skeleton.py](file:///d:/veylith/tests/end_to_end/test_walking_skeleton.py#L32-L37) | 2026-10-18 |
| | Exclusion policy (VCS, caches, node_modules) | implemented | [test_walking_skeleton.py](file:///d:/veylith/tests/end_to_end/test_walking_skeleton.py) | 2026-10-18 |
| | Secret scanner integration (redacted locations) | partial | [test_redaction.py](file:///d:/veylith/tests/unit/test_redaction.py) | 2026-10-18 |
| | Dependency inventory & CycloneDX SBOM export | not started | - | - |
| | Trojan Source / confusable filename detection | not started | - | - |
| **Protection** | Source distribution hygiene (maps, docstrings, debug) | implemented | [test_hygiene.py](file:///d:/veylith/tests/unit/test_hygiene.py) | 2026-10-18 |
| | JS/TS bundling & minification (esbuild/terser) | not started | - | - |
| | Safe Python identifier renaming (LibCST scope-aware) | not started | - | - |
| | Reflection & dynamic lookup preservation | not started | - | - |
| | Reversible transformation records & output isolation | implemented | [test_walking_skeleton.py](file:///d:/veylith/tests/end_to_end/test_walking_skeleton.py#L39-L55) | 2026-10-18 |
| | Behavioral equivalence validation (visible & held-out) | implemented | [test_walking_skeleton.py](file:///d:/veylith/tests/end_to_end/test_walking_skeleton.py#L57-L66) | 2026-10-18 |
| **Integrity** | Local Ed25519 keygen with secure permissions (0600) | not started | - | - |
| | DSSE canonical envelope signing (RFC 8785 JCS) | not started | - | - |
| | Manifest verification (`verify-manifest`) & tamper detection | implemented | [test_walking_skeleton.py](file:///d:/veylith/tests/end_to_end/test_walking_skeleton.py#L68-L77) | 2026-10-18 |
| | Key rotation & monotonic rollback detection | not started | - | - |
| **Providers** | Provider interface & contract test suite | not started | - | - |
| | Built-in provider: `fixture-strings` | not started | - | - |
| | Built-in provider: `fixture-symbols` | not started | - | - |
| | Built-in provider: `sourcemap-recovery` | not started | - | - |
| | Built-in provider: `metadata-leaks` | not started | - | - |
| | REA adapter: allowlist/denylist enforcement | not started | - | - |
| | REA adapter: safe CLI/stdio subprocess execution | not started | - | - |
| | REA adapter: recorded fixture mode & unavailable reporting | not started | - | - |
| **Benchmark** | Harmless deterministic corpus with ground truth | not started | - | - |
| | Tri-state metric system (`Measured`, `Unavailable`, `N/A`) | implemented | [models/base.py](file:///d:/veylith/src/veylith/models/base.py#L16-L39) | 2026-10-18 |
| | Multi-run statistics & uncertainty quantification | not started | - | - |
| | Run comparison & delta analysis (`veylith compare`) | not started | - | - |
| **LLM Evaluator** | Deterministic subject-agent test harness | not started | - | - |
| | Mock sensitive tool server & canary token tracing | not started | - | - |
| | Deterministic oracle for prompt-injection resistance | not started | - | - |
| | Self-application safety test for Veylith core | not started | - | - |
| **Evidence** | Evidence record graph & DAG validation | not started | - | - |
| | Unverified claim detection & contradiction tracking | not started | - | - |
| **Sandbox** | Sandbox backend interface & Podman/Docker adapter | not started | - | - |
| | Resource limits (caps, network none, ro fs, pids, mem) | not started | - | - |
| | Cleanup & cancellation signal handling | not started | - | - |
| **Reporting** | JSON canonical report export | implemented | [test_walking_skeleton.py](file:///d:/veylith/tests/end_to_end/test_walking_skeleton.py#L79-L84) | 2026-10-18 |
| | Markdown report generator with output escaping | implemented | [test_walking_skeleton.py](file:///d:/veylith/tests/end_to_end/test_walking_skeleton.py#L79-L84) | 2026-10-18 |
| | SARIF code-scanning export | not started | - | - |
| | CI Policy Gate (`veylith gate`) | not started | - | - |
| | Claims linter (`veylith.reporting.claims_lint`) | implemented | [test_claims_lint.py](file:///d:/veylith/tests/unit/test_claims_lint.py) | 2026-10-18 |
