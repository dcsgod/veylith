# ADR 0004: Transformation Depth Strategy for v0.1

## Context
Code transformation can introduce functional regressions if scope, exports, or dynamic reflection are improperly handled. Regex-based renaming is brittle and dangerous. We must determine the transformation depth and tools for v0.1.

## Decision
1. **Python Complete First:**
   - Use **LibCST** for scope-aware, format-preserving AST analysis and renaming.
   - Strictly rename ONLY provably local identifiers (local function names, private class attributes, internal local variables).
   - Preserve all public APIs (`__all__`), serialization fields (Pydantic/dataclasses), reflection calls (`getattr`, `setattr`, `globals()`, `locals()`), decorators, and framework entry points.
   - When reflection or dynamic lookup is detected in scope, skip renaming and record the reason in the transformation log.
2. **JavaScript Distribution Hygiene & Bundling:**
   - Distribution hygiene (removal of `.map` files, dev configs, tests, docstrings) supported out-of-the-box.
   - Bundling and minification with property mangling **disabled by default**. Property mangling requires explicit opt-in and reserved name lists.
   - JS identifier renaming at AST level deferred until Python pipeline is completely verified.

## Alternatives Considered
- Regex-based text replacement: Explicitly forbidden by specification §9A.
- Blind symbol obfuscation: High risk of runtime breaks in dynamically typed languages.

## Consequences
- Guaranteed preservation of semantic behavior on public APIs and reflection.
- Every skipped identifier has an auditable log entry explaining why safety required skipping.
