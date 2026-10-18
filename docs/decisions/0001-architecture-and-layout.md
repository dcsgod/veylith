# ADR 0001: Architecture & Repository Layout

## Context
Veylith requires a modular, production-grade structure supporting CLI commands, an intake and inventory pipeline, a protection engine, integrity verification, local and external analysis providers, evaluation benchmarks, and reporting. The architecture must strictly uphold security boundaries: immutability of originals, untrusted input containment, isolated outputs, deterministic hashing, and typed error handling.

## Decision
We structure Veylith as a Python 3.11+ project using `hatchling` as the build backend, `uv` for dependency management and locking, and Typer for the CLI. The package layout is:
- `src/veylith/`: Core library code with strict domain separation (`safety`, `intake`, `inventory`, `protection`, `transformations`, `integrity`, `providers`, `evaluation`, `llm_security`, `sandbox`, `reporting`, `storage`).
- `schemas/`: Versioned JSON schemas automatically exported from Pydantic v2 models.
- `tests/`: Multi-tiered testing suite (unit, integration, security, end-to-end, contract, fixtures).
- `docs/decisions/`: Architecture Decision Records (ADRs) tracking all major design choices.

Circular dependencies are banned. All modules must adhere to `mypy --strict`.

## Alternatives Considered
- Monolithic single-module CLI: Rejected due to inability to independently test, mock, or sandbox components.
- Plugin-only framework: Rejected as too complex for core v0.1 deliverables, though providers will use entry-point discovery.

## Consequences
- Clean separation of concerns and clear safety boundaries.
- Every module can be independently tested with unit and contract tests.
- High developer velocity and auditability.
