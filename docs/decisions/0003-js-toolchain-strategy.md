# ADR 0003: JavaScript/TypeScript Toolchain Strategy

## Context
Veylith supports JavaScript and TypeScript project evaluation, hygiene, bundling, and minification. Running JS toolchains requires Node.js, esbuild, Terser, or Babel. However, Veylith is fundamentally a Python application and must run without requiring Node.js to be installed for non-JS workflows.

## Decision
We make **Node.js and JS tools optional runtime dependencies**:
1. Core distribution hygiene (source map removal, file stripping, secret scanning) is implemented natively in Python without requiring Node.js.
2. Advanced bundling and minification delegate to `esbuild` or `Terser` via pinned subprocesses when Node.js is present.
3. `veylith doctor` checks and reports Node.js and npm/npx availability. If Node is absent, JS bundling is reported as `unavailable (Node.js runtime not found)` rather than crashing or terminating the entire tool.

## Alternatives Considered
- Requiring Node.js as a mandatory prerequisite for installing Veylith: Rejected, as users protecting Python or native projects should not need Node.js.
- Bundling a standalone Python-only JS minifier (e.g. `rjsmin`): Rejected for production bundling because it lacks AST-aware bundling, module resolution, and TypeScript transpilation.

## Consequences
- Veylith installs cleanly in pure Python environments.
- JS projects can be evaluated for hygiene natively.
- Full JS bundling is activated when Node is available, with explicit capability reporting.
