# ADR 0006: Sandbox Isolation Architecture

## Context
Executing untrusted software or dynamic analysis tools (such as runtime observation or candidate reconstruction tests) introduces host compromise risks. Dynamic execution must only occur inside an isolated, disposable sandbox with hardened limits and explicit operator authorization.

## Decision
1. **Container Backend Default (Rootless Podman / Docker):**
   - The primary sandbox backend uses rootless Podman (or Docker when configured) with:
     - `--network none` (no network connectivity)
     - Read-only root filesystem (`--read-only`)
     - Dropped capabilities (`--cap-drop ALL`)
     - Prevention of privilege escalation (`--security-opt no-new-privileges`)
     - Dedicated non-root user
     - CPU, memory, and PID limits (`--pids-limit`, `--memory`, `--cpus`)
     - Isolated tmpfs scratch spaces
   - All state is wiped upon completion or cancellation.
2. **Backend Abstraction & Honest Reporting:**
   - A `SandboxBackend` abstract interface decouples specific container runtimes.
   - `veylith doctor` reports sandbox availability and isolation strength.
   - If no secure container sandbox is available and dynamic execution is requested, Veylith **fails with exit code 8** rather than silently falling back to insecure host execution.
3. **Cancellation & Cleanup:**
   - SIGINT/SIGTERM triggers deterministic cleanup of containers, temp directories, and processes.

## Alternatives Considered
- Direct host execution: Strictly rejected for untrusted artifacts and dynamic analysis.
- Virtualenv/subprocess isolation: Documented as inadequate isolation for untrusted code execution.

## Consequences
- Operator hosts are protected from untrusted execution.
- Clear error reporting if sandboxing tools are missing.
