# G0 Book 9 — Runtime Substrate ADR

**Chapter:** B9.C6
**Date:** 2026-08-27
**Status:** `OCE_NATIVE` (ratified)

## Decision

Select **Candidate A — OCE-native / project-owned runtime**: the Grant
machine runs on its own project-owned runtime (Python 3.11, in-repo
contracts, plain-JSON durable records), with Postgres as canonical state,
object storage for artifacts/snapshots, and the governed Model Gateway for
model execution.

**Status value:** `OCE_NATIVE` — one of the four allowed outcomes
(`OCE_NATIVE | COMPOZY_BOUNDED | QM_BOUNDED | HYBRID_BOUNDED`). No `TBD`.

## Why the winner won

1. **Passes all 15 constitutional hard gates on measured evidence.** Every
   other candidate failed gate 7 (framework-owned state risks dual
   sovereignty with canonical Postgres ownership) or was unproven on 13+
   gates with no in-repo integration to test.
2. **Removes the most generic engineering while changing the least product
   architecture.** The G0 kernel already IS the runtime: deny-by-default
   Authorizer, DecisionRegistry, ToolGateway, governed Model Gateway,
   ApprovalRegistry, tenant/project/resource scope, durable stage records,
   cold reconstruction, telemetry. Selecting a foreign substrate would add
   an adapter layer for every contract with zero measured benefit.
3. **Evidence:** 1,778-test suite, live model lane, full vertical slice,
   amendment drill, cold restart, degraded mode, 6/6 security denials —
   all MEASURED in this repository.
4. **Local-first and export-friendly:** no external daemon, no framework
   lock-in; exit cost is the cost of the plain-Python code already owned.

## Why each loser lost

- **CompozyOS (Candidate B):** DISQUALIFIED at hard gate 7 — its
  durable-session/control state is framework-owned and would compete with
  canonical Postgres ownership for workflow truth (Book 9 §3: "No external
  runtime may create a second sovereign… workflow truth"). Unproven on 13
  other gates. Not installed (BLOCKED in this environment). Per Amendment
  002 Batch 04 ledger: `DEFER (no adoption)`.
- **QM (Candidate C):** DISQUALIFIED at hard gate 7 — framework-owned
  session/sandbox state risks the same dual sovereignty. Unproven on 13
  other gates. Not installed (BLOCKED). Ledger: `DEFER (reference only)`.
- **Hybrid (Candidate D):** No narrow component is installed or adoptable
  here; adding one now is speculative glue with zero measured benefit at
  G0. Not selected — re-evaluate only when a measured G1 workload
  justifies it.

## What parts are used

- The in-repo G0 runtime: `prototype/g0/security/` (authorization, identity,
  tool gateway), `prototype/g0/model/` (governed model gateway),
  `prototype/g0/vslice/` (vertical slice), `prototype/g0/evidence/`
  (DecisionRecord), `prototype/g0/evaluation/` (Book 7 evaluation),
  `prototype/g0/domain/` (grant domain contracts).
- Python 3.11 stdlib + `requests` (only external runtime dependency).
- Postgres (canonical, per C7 ownership matrix) and object storage
  (artifacts/snapshots) as the G1 persistence adapters.

## What parts are explicitly NOT used

- No Compozy daemon, no QM runtime, no external agent framework.
- No framework-owned canonical state, no framework-owned policy, no
  framework-owned memory, no autonomous submission, no self-modification.
- No Kubernetes/service-mesh at G0 (deployment strategy C16 is
  containerized services + managed Postgres; K8s only if measured evidence
  later justifies it).
- No trading-domain/OCE trading baggage in the Grant repo (C10 hard rule).

## What remains (honest G1 boundary)

- Production durable-execution substrate: task/run table, queue, scheduler,
  checkpoint/resume at the application layer (G1.1 Platform kernel). The
  G0 record-level durability and cold-restart reconstruction are the
  foundation; the production task table is not yet built.
- Postgres and object-storage adapters (G1.2 domain persistence, G1.7
  artifacts).
- Production secret management replacing `DevRuntimeCredentialResolver`
  (DEV_RUNTIME_ONLY → G1.10 operations hardening).

## Exit strategy / replacement boundary

- Because the runtime is project-owned plain Python + JSON records, exit
  cost is minimal: export semantic state (records, decisions, evidence
  refs) is already the repo format.
- If a future measured G1 workload justifies an external durable-execution
  component, it must be added as an ADAPTER behind our TaskContract and
  must re-pass all 15 hard gates; it can never own canonical state.

## License implications

- All G0 runtime code is project-owned (in-repo). `requests` is Apache-2.0;
  the only external runtime dependency (see `G0_B9_DEPENDENCY_MANIFEST.md`).
- OpenRouter is a provider adapter (per-call API), not a runtime dependency.
- No proprietary framework license obligations introduced.

## Operational consequences

- Operations own plain-Python services: no external daemon to operate,
  upgrade, or be held hostage by upstream churn.
- Model provider remains replaceable (adapter registry).
- Postgres + object storage are the only externally operated components,
  both commodity.
