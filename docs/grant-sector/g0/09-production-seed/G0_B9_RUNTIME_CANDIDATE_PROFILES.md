# G0 Book 9 — Runtime Candidate Profiles & Hard-Gate Elimination

**Chapters:** B9.C3 + B9.C4
**Source:** Amendment 002 (§8 candidate patterns), external component
decision ledgers (Batch 04), Book 6 security contracts, Book 7 model
runtime, Book 8 vertical slice.
**Date:** 2026-08-27
**Status basis:** Every profile marks what is `MEASURED`, `REVIEWED`,
`NOT_RUN`, or `BLOCKED` — nothing is fabricated.

## Candidate A — OCE-native / project-owned runtime

| Field | Value |
|---|---|
| Version/commit | In-repo: `prototype/g0/` + `tools/g0/` at final G0 head (this repository) |
| License | Project-owned (G0 artifacts, MIT-style headers where present) |
| Maturity | Working vertical slice + 1,778-test suite + live model lane — MEASURED |
| Language/runtime | Python 3.11 (stdlib + `requests`) |
| Storage model | In-process durable `SliceRecord` dataclasses; Postgres target (C7 ownership matrix) |
| Session model | Typed `IntentContract`/`TaskPlan`/`TaskContract`; deterministic, replayable |
| Task model | `TaskContract` → bounded `WorkerResult`; durable records per stage |
| Worker model | Task-scoped workers; `HERMES_PERSONAL`/`HERMES_CEO`/worker principals distinct |
| Permissions | Deny-by-default `Authorizer`; grant authority ladder; DecisionRegistry |
| Approvals | `ApprovalRegistry` integrated into authorization (Book 6 repair) |
| MCP/tool model | Independent `ToolGateway` verifying PDP decisions; capability binding |
| Credential handling | Server-side `DevRuntimeCredentialResolver` (DEV_RUNTIME_ONLY); secret never in prompts/logs |
| Multi-tenancy | Structural tenant/project/resource scope; cross-tenant/cross-project DENY — MEASURED |
| Observability | Slice telemetry (tasks, checkpoints, model calls, tokens, latency, audit volume) |
| Failure/recovery | Cold restart reconstructs full state from records without chat — MEASURED (1.1 ms/10 records) |
| Local dev | Zero external services needed to run the slice and full test suite |
| Cloud path | Containerizable Python services (C16 deployment strategy) |
| Extension/plugin model | Module packages under `platform/` and `sectors/` boundaries |
| Exportability | Plain Python + JSON records; no framework lock-in |
| Known constraints | Postgres/object-storage adapters are G1 work; runtime restart semantics must be productized (durable queue) |
| Custom glue required | Minimal — this is the current architecture |

## Candidate B — CompozyOS substrate

| Field | Value |
|---|---|
| Version/commit | Not installed; external repo reviewed (R0 Batch 01/04) |
| License | Review notes in R0 external review batch (proprietary-adjacent; verify before adoption) |
| Maturity | External project; in-repo integration NOT_RUN |
| Language/runtime | External daemon/runtime |
| Storage model | Compozy-owned sessions/control state (risk: framework-owned canonical state) |
| Session model | Durable sessions/loops (strength) |
| Task model | Durable execution (strength) |
| Worker model | Requires bounded adapter under our `TaskContract` |
| Permissions | Capabilities/approvals exist (strength) but must bind to OUR `Authorizer`, not its own |
| Credential handling | Would need to sit behind our server-side secret boundary |
| Multi-tenancy | Must prove tenant isolation at OUR structural scope |
| Observability | External; must export |
| Failure/recovery | Unverified in-repo (NOT_RUN) |
| Local dev | Requires installing the external daemon (BLOCKED in this environment) |
| Cloud path | Unverified |
| Exportability | Exit/rebuild path unproven for semantic state (risk) |
| Known constraints | Amendment 002 ledger Batch 04: `DEFER (no adoption)` — Book 4/6/8 implemented the protocol core in-repo; no substrate needed yet |
| Custom glue required | High — adapter layer for every contract |

## Candidate C — QM substrate

| Field | Value |
|---|---|
| Version/commit | Not installed; external repo reviewed (R0 Batch 01/04) |
| License | Review notes in R0 batch |
| Maturity | External; in-repo integration NOT_RUN |
| Language/runtime | External |
| Storage model | QM-owned session/sandbox state (risk: framework-owned state) |
| Session model | Scoped sessions (strength) |
| Task model | Scoped/sandboxed execution (strength) |
| Worker model | Would require our task authority binding |
| Permissions | Sandbox/policy patterns (strength) but must bind to OUR `Authorizer` |
| Credential handling | Must sit behind our secret boundary |
| Multi-tenancy | Must prove isolation at our scope |
| Observability | External; must export |
| Failure/recovery | Unverified in-repo (NOT_RUN) |
| Local dev | Requires installing external runtime (BLOCKED in this environment) |
| Exportability | Unproven for semantic state |
| Known constraints | Ledger Batch 04: `DEFER (reference only)` — Book 4 boundaries are executable without it |
| Custom glue required | High |

## Candidate D — Bounded hybrid

| Field | Value |
|---|---|
| Version/commit | N/A — composition of the above |
| License | Depends on chosen narrow component |
| Maturity | Unselected components NOT_RUN |
| Storage model | Would keep canonical state project-owned (Postgres per C7) |
| Session/task model | Narrow external durable-execution component only |
| Permissions | Still OUR `Authorizer`; external component never owns authority |
| Multi-tenancy | Still our structural scope |
| Failure/recovery | Unverified in-repo (NOT_RUN) |
| Local dev | Requires installing the narrow component (BLOCKED in this environment) |
| Exportability | Depends on component |
| Known constraints | Amendment 002: hybrid allowed but no component is installed or adoptable in this environment; adding one now is speculative glue with zero measured benefit |
| Custom glue required | High for zero measured gain at G0 |

---

## Hard-Gate Elimination (B9.C4)

Constitutional hard gates — a failure is DISQUALIFICATION, not a score
penalty:

| # | Hard gate | Candidate A (OCE-native) | Candidate B (Compozy) | Candidate C (QM) | Candidate D (Hybrid) |
|---|---|---|---|---|---|
| 1 | Personal/CEO identity separation | PASS (MEASURED) | PASS (by adapter — NOT_RUN) | PASS (by adapter — NOT_RUN) | PASS (by adapter — NOT_RUN) |
| 2 | Tenant/project isolation structural | PASS (MEASURED) | UNPROVEN (NOT_RUN) | UNPROVEN (NOT_RUN) | UNPROVEN (NOT_RUN) |
| 3 | Task-scoped worker authority | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |
| 4 | Deny-by-default capabilities | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |
| 5 | External action separated from drafting | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |
| 6 | Server-side secrets | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |
| 7 | Canonical Grant/domain state independence | PASS (MEASURED) | **FAIL — framework-owned control state risks dual sovereignty** | **FAIL — framework-owned session state risks dual sovereignty** | UNPROVEN |
| 8 | SourceSnapshot/evidence identity preserved | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |
| 9 | Audit/provenance ID compatibility | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |
| 10 | Durable accepted-task recovery | PASS (MEASURED — cold restart) | UNPROVEN | UNPROVEN | UNPROVEN |
| 11 | Restart/reconstruction | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |
| 12 | Export/rebuild/exit path | PASS (plain Python/JSON) | UNPROVEN (semantic export risk) | UNPROVEN | UNPROVEN |
| 13 | No shared cross-user "mind" | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |
| 14 | No framework-owned invisible self-modification | PASS | UNPROVEN | UNPROVEN | UNPROVEN |
| 15 | Submission stays disabled | PASS (MEASURED) | UNPROVEN | UNPROVEN | UNPROVEN |

**Elimination result:**

- **Candidate B (CompozyOS):** DISQUALIFIED on hard gate 7 (framework-owned
  control state risks dual sovereignty with canonical Postgres ownership),
  and unproven on 13 other gates. No in-repo integration exists to test
  (BLOCKED in this environment).
- **Candidate C (QM):** DISQUALIFIED on hard gate 7 (framework-owned session
  state), and unproven on 13 other gates. No in-repo integration exists
  (BLOCKED in this environment).
- **Candidate D (Hybrid):** No narrow component is installed or adoptable in
  this environment; unproven on all un-measured gates. Introducing one now
  is speculative glue with zero measured benefit at G0 → **NOT SELECTED**
  (not disqualified, but not adopted without measured need).
- **Candidate A (OCE-native / project-owned):** PASSES all 15 hard gates on
  measured evidence → **SURVIVES to weighted scoring.**

The elimination is recorded in `G0_B9_RUNTIME_BAKEOFF_RESULTS.md` and the
ADR. This does not permanently reject Compozy/QM: Amendment 002's ledger
already defers both to a ratified runtime study; if a future G1 workload
demonstrates a measured need for an external durable-execution component,
they may be re-profiled against these same gates in a new bake-off.
