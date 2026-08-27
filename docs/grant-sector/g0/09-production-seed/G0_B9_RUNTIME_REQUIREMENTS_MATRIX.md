# G0 Book 9 — Production Runtime Requirements Matrix

**Chapter:** B9.C2
**Source:** Books 1–8 master plans, constitutional invariants, Book 8
workload evidence (`G0_B9_BOOK8_WORKLOAD_EVIDENCE.md`).
**Date:** 2026-08-27

Every requirement: `requirement_id`, `source_book`, `hard_gate`,
`priority`, `book8_evidence_ref`, `acceptance_test`.

## Identity / scope

| requirement_id | requirement | source_book | hard_gate | priority | evidence_ref | acceptance_test |
|---|---|---|---|---|---|---|
| REQ-ID-001 | User identity distinct from agent identity | B4, B6 | true | P0 | slice principal model | Personal, CEO, worker principals are distinct; no cross-role reuse |
| REQ-ID-002 | Personal Hermes identity ≠ CEO Hermes identity ≠ worker identity | B4, B7 | true | P0 | model runtime tests (PERSONAL/CEO profiles) | same principal cannot hold both Personal and CEO roles |
| REQ-ID-003 | Tenant/project/resource scope structural on every write | B6, B8 | true | P0 | security drills (cross-tenant/cross-project denied) | cross-tenant access returns DENY in the real topology |
| REQ-ID-004 | Service identity for background jobs and adapters | B6, B9 | false | P1 | — | adapter runs under a scoped service principal |

## Durable execution

| requirement_id | requirement | source_book | hard_gate | priority | evidence_ref | acceptance_test |
|---|---|---|---|---|---|---|
| REQ-DUR-001 | Accepted task persisted before acknowledgement | B5, B8 | true | P0 | SliceRecord durability | kill process mid-task → task recoverable from durable record |
| REQ-DUR-002 | Checkpoint/resume for long tasks | B8 (W3) | true | P0 | checkpoint_count=6 per slice | long research task resumes after restart |
| REQ-DUR-003 | Restart recovery (cold reconstruction) | B8 (C33) | true | P0 | reconstruction 1.1ms/10 records, raw_chat_required=false | fresh process reconstructs full slice state |
| REQ-DUR-004 | Bounded retries with idempotency | B5, B8 | true | P0 | model bounded retry | duplicate delivery does not duplicate consequential state |
| REQ-DUR-005 | Background jobs (source refresh, revision watch) | B8 (W6) | false | P1 | source fetches=3 | scheduled refresh updates a snapshot revision |
| REQ-DUR-006 | Selective downstream invalidation on revision change | B2, B8 (C29) | true | P0 | amendment drill (6 stages invalidated, history preserved) | material revision invalidates only stale-anchored stages |

## Agent execution

| requirement_id | requirement | source_book | hard_gate | priority | evidence_ref | acceptance_test |
|---|---|---|---|---|---|---|
| REQ-AG-001 | Hermes executes with bounded context injection | B4, B7 | true | P0 | ContextBundle ~250 tokens/section | Personal gets client context, not raw transcript |
| REQ-AG-002 | Worker sandbox: task-scoped authority, no client contact unless permitted | B4, B8 | true | P0 | bounded_worker_pass | worker cannot reach outside its TaskContract |
| REQ-AG-003 | Structured result return (WorkerResult) | B4, B8 | true | P0 | drafting WorkerResults | every worker returns a schema-valid result |
| REQ-AG-004 | No shared cross-user "mind" / memory pollution | B4, B7 | true | P0 | memory eval (cross-project bleed) | two tenants' Hermes memories are disjoint |
| REQ-AG-005 | Sidechain storage for multi-step reasoning | B5, B8 | false | P1 | — | sidechain refs resolve after restart |

## Policy / tool control

| requirement_id | requirement | source_book | hard_gate | priority | evidence_ref | acceptance_test |
|---|---|---|---|---|---|---|
| REQ-POL-001 | Capability registry with deny-by-default authorization | B6 | true | P0 | Book 6 seam probes | unlisted capability → DENY |
| REQ-POL-002 | Grant authority ladder enforced | B6 | true | P0 | authority ladder tests | L4/L2/L4 → DENY |
| REQ-POL-003 | Independent Tool Gateway verifying PDP decisions | B6 | true | P0 | gateway tests (forged decision denied) | caller cannot pass raw AuthorizationDecision JSON |
| REQ-POL-004 | Server-side secrets; never in prompt/logs | B6, B7 | true | P0 | model runtime tests G/H/I (leak check) | secret absent from response, logs, model context |
| REQ-POL-005 | Egress control (SSRF protection) | B6, B7 | true | P0 | model gateway SSRF denial | arbitrary base URL / metadata endpoint denied |
| REQ-POL-006 | Approval registry integration | B6 | true | P0 | approval seam tests | approval-gated op requires registry-validated approval |
| REQ-POL-007 | Submission capability structurally disabled | B6, B7, B8 | true | P0 | submission_enabled=false in locks | no code path can set submission_enabled=true |

## Data / evidence

| requirement_id | requirement | source_book | hard_gate | priority | evidence_ref | acceptance_test |
|---|---|---|---|---|---|---|
| REQ-DAT-001 | Canonical domain/workflow state owned by Postgres | B5, B9 | true | P0 | ownership matrix (C7) | runtime/agent cannot mutate canonical state directly |
| REQ-DAT-002 | Immutable SourceSnapshots | B5, B8 | true | P0 | snapshot identity tests | snapshot content never rewritten |
| REQ-DAT-003 | Evidence lineage reconstructable | B5, B8 | true | P0 | reconstruction report | every material claim resolves to evidence refs |
| REQ-DAT-004 | DecisionRecord replayable | B5, B8 | true | P0 | DecisionRecord tests | same inputs → same decision |
| REQ-DAT-005 | Artifacts in object storage, versioned | B7, B8 | true | P0 | ArtifactVersion N/N+1 | artifact versions are immutable + linked |
| REQ-DAT-006 | Graph/vector projections rebuildable, non-sovereign | B5, B9 | false | P1 | — | rebuild from canonical state yields equivalent index |

## Evaluation / promotion

| requirement_id | requirement | source_book | hard_gate | priority | evidence_ref | acceptance_test |
|---|---|---|---|---|---|---|
| REQ-EV-001 | Shadow/canary runs with candidate versioning | B7 | false | P1 | shadow/canary tests | candidate runs alongside baseline without affecting it |
| REQ-EV-002 | Rollback to known-good candidate | B7 | true | P0 | rollback tests | promotion undo restores prior candidate |
| REQ-EV-003 | Eval fixture execution (golden sets) | B7 | false | P1 | golden-set tests | eval corpus versioned + reproducible |

## Operations

| requirement_id | requirement | source_book | hard_gate | priority | evidence_ref | acceptance_test |
|---|---|---|---|---|---|---|
| REQ-OPS-001 | Observability: correlation id request→intent→task→worker→decision→artifact | B8, B9 | false | P1 | telemetry | a trace spans the full slice |
| REQ-OPS-002 | Backup/recovery of canonical DB + artifacts | B9 | true | P0 | recovery plan (C20) | DB restore test passes |
| REQ-OPS-003 | Local-first development (no paid cloud for core) | B9 | false | P1 | local dev strategy (C15) | fresh clone bootstraps core flow locally |
| REQ-OPS-004 | Deployment reproducible, migration ordering + rollback | B9 | false | P1 | deployment strategy (C16) | release identifies commit + migration version + rollback target |
| REQ-OPS-005 | Cost control: configurable model cost scenarios | B9 | false | P2 | cost envelope (C23) | cost per scenario computable |

## Gate summary

Hard-gate requirements (P0): 22. Any runtime candidate failing a hard gate
is disqualified before weighted scoring (B9.C4).
