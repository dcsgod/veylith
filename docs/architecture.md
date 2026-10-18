# Veylith — Architecture Specification

## 1. System Overview

Veylith is structured as a pipeline of decoupled, testable, typed Python modules operating under strict trust boundaries.

```
+-------------------------------------------------------------------------------+
|                                  CLI (Typer)                                  |
|         init, inspect, inventory, protect, verify, benchmark, report, gate     |
+-------------------------------------------------------------------------------+
         |                     |                     |                   |
         v                     v                     v                   v
+-----------------+   +-----------------+   +-----------------+   +-------------+
| Intake & Safety |   | Protection      |   | Evaluation &    |   | Reporting & |
| - Path Guard    |   | - Pipeline      |   | Providers       |   | Export      |
| - Manifest /    |   | - Transformations|  | - Exposure Prov.|   | - JSON      |
|   Hashing       |   | - LibCST Rename |   | - REA Adapter   |   | - Markdown  |
| - Secret Scan   |   | - Hygiene       |   | - Benchmark     |   | - SARIF     |
| - SBOM          |   | - Integrity/DSSE|   | - LLM Evaluator |   | - CI Gate   |
+-----------------+   +-----------------+   +-----------------+   +-------------+
         |                     |                     |                   |
         +---------------------+---------------------+-------------------+
                               |
                               v
               +-------------------------------+
               | Storage & Evidence Graph      |
               | - SQLite Migrations           |
               | - Pydantic Schemas            |
               | - Evidence Validation DAG     |
               +-------------------------------+
```

## 2. Core Modules & Boundaries

1. **`veylith.safety`**:
   - Path traversal guard (`PathGuard`) enforcing root containment, resolving symlinks safely, preventing TOCTOU.
   - Target content sanitizers (ANSI escape stripping, markdown delimiter sanitization).
   - Secret redaction stream filters for logs and error messages.
2. **`veylith.intake` & `veylith.inventory`**:
   - Safe directory scanner and archive unpacker with compression ratio limits.
   - Canonical SHA-256 manifest calculator (RFC 8785 normalized ordering).
   - Secret pattern scanner and dependency lockfile analyzer.
3. **`veylith.protection` & `veylith.transformations`**:
   - Source distribution hygiene: strip maps, debug statements, docstrings.
   - Scope-aware identifier renaming using `LibCST` (preserving `__all__`, reflection, exports).
   - Transformation ledger: records inputs, outputs, parameters, determinism, and rollback handle.
4. **`veylith.integrity`**:
   - Ed25519 cryptographic signing over JCS canonical statements (RFC 8785) in DSSE envelope.
   - Independent verification engine (`verify-manifest`) detecting tampering, addition, deletion, or replay.
5. **`veylith.providers`**:
   - Abstract `Provider` interface: healthcheck, capabilities, timed isolated execution.
   - Built-in local exposure providers: `fixture-strings`, `fixture-symbols`, `sourcemap-recovery`, `metadata-leaks`.
   - `rea` adapter: allowlist-governed read-only execution, hard denylist (`setup`, `update`), recorded fixtures.
6. **`veylith.evaluation` & `veylith.llm_security`**:
   - Behavioral equivalence testing on visible vs. held-out test vectors.
   - Reconstruction pass rate scoring.
   - Subject-agent prompt injection test harness with mock tools and canary token leak detection.
7. **`veylith.reporting`**:
   - Versioned JSON report schema, Markdown generator, SARIF converter, and CI gate evaluator.
   - Claims linter (`veylith.reporting.claims_lint`) enforcing policy compliance.

## 3. Data Integrity & Trust Flow
- Input content is strictly READ-ONLY. Original directories are never modified in-place.
- All transformations write to isolated, caller-specified output directories.
- All external tool outputs (including REA) are labeled `tool_reported_fact` until independently validated.
- Any unavailable capability emits `unavailable` with reason, never pseudo-numerical scores.
