# Veylith

**Tagline:** Save your software from REA.  
**Category:** AI-assisted software protection, exposure measurement, and reconstruction-resistance evaluation.  
**Mission:** Make unauthorized software reconstruction measurably harder, show software owners exactly what an analysis pipeline can still recover, and back every claim with reproducible evidence instead of promises.

> **Positioning Note:** REA (https://github.com/morluto/rea, MIT) is a legitimate, dual-use reverse-engineering toolkit. In Veylith it serves as the reference benchmark for what a capable agentic analysis pipeline can recover from software the operator owns. Veylith never disparages REA or claims to defeat it. We report findings as "measured against REA version X on sample Y".

---

## Capabilities & Verification Status

In accordance with Veylith's strict claims policy, only capabilities verified by automated tests in [STATUS.md](STATUS.md) are claimed. All other controls are marked `unverified`.

- **Current Stage:** Phase 0 (Walking Skeleton)
- **Status Ledger:** See [STATUS.md](STATUS.md) for individual capability statuses and test proofs.

---

## Installation & Development Setup

Veylith requires Python 3.11+ and uses `uv` for package management.

```bash
# Clone the repository
git clone https://github.com/veylith/veylith.git
cd veylith

# Install dependencies in editable mode
uv sync --all-extras

# Run verification suite
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src tests
uv run pytest
```

---

## Architecture & Threat Model

- [Threat Model & Attacker Tiers](docs/threat-model.md)
- [Architecture Overview](docs/architecture.md)
- [Architecture Decision Records (ADRs)](docs/decisions/)
- [Working Agreements](CLAUDE.md)

---

## License

Veylith is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
