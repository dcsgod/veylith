# Veylith — Threat Model & Attacker Tiers

## 1. Purpose and Philosophy
Veylith is an AI-assisted software protection, exposure measurement, and reconstruction-resistance evaluation system. Its mission is to make unauthorized software reconstruction measurably harder, quantify residual exposure, and back every claim with reproducible evidence.

Veylith explicitly rejects security-through-obscurity claims. Client-side controls can delay, increase cost, and defeat automated reconstruction, but cannot stop a fully-resourced, skilled human with local access.

---

## 2. Attacker Tiers

Every protection control, test claim, and benchmark metric in Veylith MUST be scoped to a specific attacker tier. A result without an assigned tier is invalid.

| Tier | Attacker Name | Capabilities & Tools |
|---|---|---|
| **T0** | Casual Observer | Inspects shipped files, runs `strings`/`grep`, views plain source, opens archives in standard file managers or text editors. |
| **T1** | Static Tooling | Uses decompilers (Ghidra, Hopper, IDA, JADX), AST analyzers, bytecode disassemblers, source-map extractors, dependency graphers. |
| **T2** | Agentic Static (REA-style) | Orchestrates T1 tools using an LLM agent with multi-step reasoning, tool-use loops, de-obfuscation synthesis, and dependency-driven reconstruction. |
| **T3** | Dynamic / Runtime Observer | Operates debuggers, dynamic binary instrumentation (Frida), memory dumpers, network traffic interceptors, and behavioral test harnesses. |
| **T4** | Resourced Human Specialist | Experienced reverse engineer with arbitrary time, custom tooling, hardware probes, and financial backing. |

### In Scope vs. Out of Scope
- **Initial Target:** **T0–T2** (Casual, Static Tooling, Agentic Static).
- **Opt-In Measurement:** **T3** is measured only when the operator explicitly enables dynamic sandbox execution (§14).
- **Explicitly Out of Scope:** **T4**. No software-only client-side control reliably stops a determined human with full device access. Veylith never claims T4 resistance.

---

## 3. Protected Assets vs. Non-Protected Attributes

### What Can Be Protected (Delayed / Obfuscated / Hardened)
- Proprietary algorithms and business logic implementation details.
- Internal function, module, and variable naming semantics.
- Non-public constants and formula parameters.
- Build metadata, comments, docstrings, and developer environment artifacts.
- Supply chain provenance and release integrity.

### What Cannot Be Protected Client-Side
- Observable I/O behavior and queryable interfaces.
- Network protocols and payloads transmitted over wire.
- Output formats, UI screens, and client-visible telemetry.
- Hardcoded symmetric secrets (the only true defense is moving sensitive evaluation server-side).

---

## 4. Threat Model for Veylith Itself (Ingestion & Execution)

Because Veylith ingests untrusted codebases, archives, and external tool outputs, it must defend its own boundary against malicious targets:

1. **Path Traversal & Zip-Slip:** Archives or directory structures containing `../`, absolute paths, symlinks pointing outside target root, or junction loops. Veylith uses canonical path guards, checks `O_NOFOLLOW` / resolved targets, and strictly forbids traversal.
2. **Resource Exhaustion (Zip Bombs & Excessive Files):** Zip ratio and uncompressed size limits, recursion depth limits, file count limits.
3. **Target Content Injection:** Malicious target files containing prompt injection payloads, terminal escape sequences (ANSI injection), or markdown/HTML injection designed to alter reports. Target data is always treated as raw text and escaped.
4. **Tool Authorization Hijack:** Malicious target content attempting to trigger shell commands, download files, or mutate agent configuration. Target content never authorizes actions.
5. **Secret Leaks in Logs/Diagnostics:** Automatic redaction filters inspect all logs and stdout/stderr before emission.
6. **Subprocess Hygiene:** All child processes execute with explicit argument lists (no `shell=True`), sanitized environments (scrubbed API keys and credentials), strict timeouts, and capped output buffers.
