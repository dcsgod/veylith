# ADR 0005: Cryptographic Signing and Provenance Architecture

## Context
Protected artifacts require cryptographic verification to detect unauthorized tampering, byte modifications, unauthorized file injections, or replay of outdated releases. The signing scheme must be standard, auditable, and operate offline by default.

## Decision
1. **Local Ed25519 Cryptography:**
   - Use the standard `cryptography` Python package for Ed25519 key generation and digital signatures. No custom cryptography.
   - Private keys are stored locally with restrictive filesystem permissions (`0600`) and are excluded from VCS by default.
2. **Canonical Manifest & DSSE Envelope:**
   - Manifests are serialized to canonical JSON according to RFC 8785 (JSON Canonicalization Scheme - JCS).
   - Signatures are packaged in a Dead Simple Signing Envelope (DSSE) containing payload type, canonical payload bytes, and Ed25519 signatures.
3. **Independent Manifest Verification (`verify-manifest`):**
   - Verification recomputes all SHA-256 digests against disk, validates the Ed25519 signature against known public keys, and verifies monotonic version sequences.
   - Tamper cases (modified byte, added file, deleted file, swapped manifest, replay attack) strictly fail closed with exit code 4.
4. **Sigstore Keyless Mode:**
   - Marked as an optional extension requiring explicit network opt-in. Never required for local or air-gapped workflows.

## Alternatives Considered
- OpenSSL CLI subprocesses: Rejected due to platform portability variations and potential shell injection risks.
- Custom hash concatenation or ad-hoc signing format: Rejected; standard DSSE and RFC 8785 JCS provide interoperable provenance.

## Consequences
- Cryptographically sound release verification.
- Zero external network dependency for standard integrity checks.
- Full compatibility with in-toto and SLSA-style provenance models.
