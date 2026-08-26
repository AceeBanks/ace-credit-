# G0-B3 — Source Onboarding & Immutable SourceSnapshot (C4-C5)

## Scope

Defines the controlled **onboarding protocol** for new sources (B3.C4) and the **immutable SourceSnapshot** unit of captured outside state (B3.C5). Together they guarantee that (1) no source enters a production allowlist by accident and (2) no captured raw body or meaningful capture metadata is ever mutated in place.

## C4 — Source Onboarding & Governance Protocol

Config of truth: `config/g0/source/onboarding_snapshot.yaml` · Prototype: `prototype/g0/source/onboarding.py`

The protocol is a fixed sequence of staged gates that must ALL pass before `ENABLED`:

```
CANDIDATE → IDENTITY/OWNERSHIP CHECK → TERMS/ROBOTS/ACCESS REVIEW →
AUTHORITY CLASSIFICATION → DATA-SHAPE ANALYSIS → ADAPTER/CAPTURE STRATEGY →
FIXTURE CAPTURE → SCHEMA/PARSER TESTS → RATE-LIMIT + FAILURE TEST →
SECURITY/PROMPT-INJECTION TEST → SOURCE HEALTH POLICY → ENABLED
```

Implemented as `ONBOARDING_STAGES` (11 gates) in `SourceGovernor`. Promotion to ENABLED requires every gate to have been passed plus a populated `SourceOnboardingPacket`.

**Source statuses:** `CANDIDATE, REVIEWING, FIXTURE_ONLY, ENABLED, DEGRADED, DISABLED, RETIRED`.

### Hard rule

An agent discovering a useful site may create a `SourceCandidate` or research note. It may **never** automatically add that domain to production allowlists. Promotion flows only through the staged protocol and ends in an explicit `ENABLED`.

## C5 — Immutable SourceSnapshot

Config of truth fixtures: `config/g0/source/onboarding_snapshot.yaml` · Prototype: `prototype/g0/source/snapshot.py`

`SourceSnapshot` is a frozen dataclass carrying all 26 fields from the plan's contract. The raw body is not stored inline — it is referenced by `raw_object_uri` + `raw_hash` (default `sha256`).

**Capture methods:** `API_JSON, API_XML, BULK_FILE, HTML, PDF, DOCX, IMAGE, MANUAL_UPLOAD, USER_FORM, OTHER`.
**Snapshot statuses:** `CAPTURED, VERIFIED_INTEGRITY, PARTIAL, FAILED_CAPTURE, REDACTED, TOMBSTONED`.

### Immutability rule

No update-in-place to raw body/hash/meaningful capture metadata. `SnapshotStore.attempt_mutation()` rejects and records any mutation attempt (fail closed). Corrections create a **new** snapshot (or a metadata-correction event) with lineage via `previous_snapshot_id`/`revision_key`.

### Content addressing & deduplication

A `CaptureEvent` (a retrieval occurrence) is separated from the deduplicated raw object. Identical raw content on a later retrieval shares bytes (same `raw_hash`) while every retrieval event — with its own timing — is preserved. Changed content produces a different hash and a new snapshot lineage.

## Tests

`tests/g0/book3/test_onboarding_snapshot.py` — 16 tests covering:
- candidate never auto-enables a domain;
- unreviewed source cannot be ENABLED; promotion requires every stage;
- disabled/retired sources cannot promote or enable;
- snapshots are immutable frozen records; mutation attempts rejected + recorded;
- raw hash deterministic; identical content dedups bytes but keeps retrieval events;
- changed content creates new lineage;
- validator enforces snapshot field contract and known enums.

## Validation

- Validator CLI: `python tools/g0/validate_onboarding_snapshot.py` → **PASS**
- Book 3 suite: 35 passed (19 C2-C3 + 16 C4-C5)

## Commits

- `G0-B3-C4-C5` chapter band (this document + onboarding/snapshot protos + validator + tests).
- Includes the correction to the C2-C3 evidence doc's class table to match the actual `config/g0/source/source_classes.yaml` schema (OFFICIAL_ISSUER…DERIVED_INTERNAL with A–E tiers).

## Status

PASS — controlled onboarding and immutable snapshots are fail-closed and under test.