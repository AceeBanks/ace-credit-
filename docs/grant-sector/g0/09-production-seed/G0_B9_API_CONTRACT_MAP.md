# G0 Book 9 — API / Event Contract Map

**Chapter:** B9.C9
**Date:** 2026-08-27
**Status:** FROZEN (semantic boundaries; exact request/response shape
evolves in G1)

## REST-ish surface (G1 shape)

| Endpoint | Purpose | Scope | Gate |
|---|---|---|---|
| `POST /intent` | Client intent → IntentContract (Personal Hermes) | tenant | intent schema valid |
| `GET /opportunities/search` | Opportunity discovery + match | tenant | eligibility not overridden by ranking |
| `POST /eligibility/evaluate` | Deterministic eligibility | tenant+project+revision | rule engine only |
| `POST /applications` | ApplicationProject shell | tenant+project | project scope |
| `POST /applications/{id}/draft` | Draft generation (bounded workers) | tenant+project | QA hard gate before readiness |
| `POST /qa/run` | Claim ledger + deterministic QA | tenant+project | gates |
| `POST /artifacts/generate` | Versioned artifacts | tenant+project | artifact service |
| `POST /approvals` | Approval requests (registry-validated) | tenant+project | ApprovalRegistry |
| `POST /evaluations` | Book 7 eval run (CandidateChange) | eval identity | deterministic-first |
| `POST /promotions` | PromotionDecision (governed) | eval identity | single promotion path |
| `GET /projects/{id}/reconstruction` | Cold reconstruction report | tenant+project | records only, no raw chat |

No submission endpoint exists. `submission_enabled=false` is structural —
there is no route, capability, or tool that can set it.

## Internal events

| Event | Emitted by | Consumed by | Payload anchor |
|---|---|---|---|
| `IntentAccepted` | Personal Hermes | CEO Hermes, audit | intent_id |
| `TaskAccepted` | CEO Hermes | worker runtime | task_id, task contract ref |
| `TaskCompleted` | worker runtime | CEO synthesis, audit | worker_result ref |
| `SourceSnapshotCreated` | source ingestion | evidence registry | snapshot_id (immutable) |
| `OpportunityRevisionCreated` | source ingestion | eligibility, applications | revision_id (append-only) |
| `EligibilityInvalidated` | revision watcher | downstream stages | decision refs to invalidate (selective) |
| `ApplicationDrafted` | drafting | QA | artifact refs |
| `QACompleted` | QA | packaging | qa report ref |
| `ApprovalRequired` | policy | approvals | approval class, resource, version, action |
| `ArtifactVersionCreated` | artifact service | evaluation, client | artifact_version_id |
| `CandidateChangeProposed` | evaluation | promotion | candidate ref, baseline ref |
| `PromotionDecisionRecorded` | promotion | rollout (shadow/canary) | decision ref |

## Event rules

- Events are **signals**, never the state of record — canonical state is
  already durable in Postgres before any event is published.
- Event payloads carry refs (`intent_id`, `task_id`, `snapshot_id`,
  `decision_id`), not bodies of truth.
- `EligibilityInvalidated` carries the decision anchors to selectively
  recompute; it never triggers a global wipe (Book 8 C29 law).
