# ADR 0002: Open Source License Choice

## Context
Veylith is an open-source defensive security and evaluation tool designed to protect software and benchmark reconstruction resistance. Section 22 lists the choice between Apache-2.0 and MIT.

## Decision
We select the **Apache License 2.0** as the project license.

## Rationale & Alternatives
- **Apache-2.0 (Selected):** Provides an explicit grant of patent rights from contributors to users, includes clear trademark restrictions, and grants strong defensive termination protections if a party initiates patent litigation. For a security and transformation toolkit, patent indemnification and explicit contributor terms provide crucial legal clarity.
- **MIT:** While MIT matches REA's license, it lacks explicit patent grant terms and contributor rights definitions.

## Consequences
- The repository must include the standard Apache-2.0 `LICENSE` file.
- All source files carry appropriate standard Apache-2.0 copyright notices.
- Downstream commercial and enterprise users can adopt Veylith with patent clarity.
