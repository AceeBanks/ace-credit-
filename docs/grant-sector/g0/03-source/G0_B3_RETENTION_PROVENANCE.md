# G0-B3 — Data Retention/Deletion & End-to-End Provenance (C20-C21)

## Scope

Defines lifecycle before raw source and client data accumulate (B3.C20), and makes every material generated claim traceable to source capture (B3.C21).

## C20 — Data Retention, Deletion & Privacy Classes

Config of truth: `config/g0/source/retention_policy.yaml` · Prototype: `prototype/g0/source/retention.py`

Eight data classes govern lifecycle, from public source metadata (D0) through public raw snapshots (D1), client business data (D2), sensitive client/PII (D3), generated artifacts (D4), worker sidechains/traces (D5), audit/security records (D6) and caches/temp extraction (D7). Each class declares its retention posture and the deletion semantics it may apply.

Deletion is not a single action — it is one of `DELETE_CONTENT`, `TOMBSTONE_METADATA`, `REVOKE_ACCESS`, `ARCHIVE`, or `LEGAL_OPERATIONAL_HOLD`, and each class only allows the semantics its policy permits (e.g. audit records can be held/tombstoned but never content-deleted).

The **provenance deletion rule** is executable: deleting raw evidence changes the replay status of downstream material — `DELETE_CONTENT` → `NON_REPLAYABLE`, `TOMBSTONE_METADATA` → `PARTIAL_REPLAY`, `REVOKE_ACCESS` → `ACCESS_REVOKED`, while `ARCHIVE`/`LEGAL_OPERATIONAL_HOLD` preserve replayability. A tenant delete scrubs sidechains/cache rows for that tenant, and audit metadata persists without embedding the raw secret/PII fixture content.

## C21 — Provenance Chain Specification

Config of truth: `config/g0/source/provenance_chain.yaml` · Prototype: `prototype/g0/source/provenance.py`

The minimum chain, in order: SourceRegistry → CaptureEvent/SourceSnapshot → ExtractionEvent → NormalizationEvent → EvidenceClaim/ExternalIdentifier/StatisticObservation → PromotionEvent/CanonicalFact → EligibilityDecision/MatchExplanation/ResearchFinding → RequirementResponse/ProposalSection/BudgetLine → ArtifactVersion/SubmissionPackage.

A `ProvenanceGraph` stores typed `ProvenanceEdge`s with one of eleven relationships (`CAPTURED_FROM`, `EXTRACTED_FROM`, `NORMALIZED_FROM`, `SUPPORTED_BY`, `CONTRADICTED_BY`, `DERIVED_FROM`, `USED_IN`, `SATISFIES`, `GENERATED_FROM`, `SUPERSEDES`, `INVALIDATED_BY`).

**Trace rule (fail-closed):** given a material proposal sentence/assertion, the product must trace to source capture. A trace with no edges, an orphaned node, a missing `CAPTURED_FROM` terminal, or a missing critical hop (`CaptureEvent_SourceSnapshot`, `NormalizationEvent`, `EvidenceClaim_...`) is a FAIL. The chain replays from stored provenance edges alone — no agent memory required.

## Tests

- `tests/g0/book3/test_retention.py` — D0..D7 present, deletion semantics, replay-status changes per deletion semantic, D6 cannot content-delete, tenant delete scrubs sidechains/cache, audit never retains raw secrets;
- `tests/g0/book3/test_provenance.py` — material claim traces to source capture; missing extraction hop / orphan / missing capture terminal all FAIL; contradictions expressible; critical hops defined.

## Validation

- `python tools/g0/validate_retention_provenance.py` → **PASS**

## Commits

- `G0-B3-C20-C21` chapter band.

## Status

PASS — lifecycle is classed and deletion-safe, and every material claim can trace end-to-end to source capture or fail loudly.
