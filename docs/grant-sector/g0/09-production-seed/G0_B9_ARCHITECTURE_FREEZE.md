# G0 Book 9 — Architecture Decision Freeze

**Chapter:** B9.C28
**Date:** 2026-08-27
**Status:** FROZEN — no unresolved P0 TBD.

## ADR index

| Decision | Status | Reference |
|---|---|---|
| Runtime substrate | **RATIFIED** — `OCE_NATIVE` (project-owned) | `G0_B9_RUNTIME_SUBSTRATE_ADR.md` |
| Canonical DB | **RATIFIED** — Postgres | `G0_B9_CANONICAL_STATE_OWNERSHIP.md` |
| Immutable payloads | **RATIFIED** — object storage (S3-compatible) | same |
| Redis/queue role | **RATIFIED** — transport/cache/leases/rate-limits only, non-authoritative | same |
| Graph projection | **PROVISIONAL_G1_VALIDATE** — rebuildable, non-sovereign; G1.5 | same |
| Vector retrieval | **PROVISIONAL_G1_VALIDATE** — rebuildable semantic index; G1.5 | same |
| Parser choice | **PROVISIONAL_G1_VALIDATE** — Book 5 lanes; production parser TBD at G1.3 | backlog |
| Evaluation tooling | **RATIFIED** — in-repo Book 7 suite; external tools subordinate adapters | `G0_B7_EXTERNAL_TOOL_BAKEOFF.md` |
| Identity/auth | **RATIFIED** — deny-by-default Authorizer, grant authority ladder, PDP-verified gateways | Book 6 + security baseline |
| Tool gateway | **RATIFIED** — independent, capability-bound, no caller JSON | Book 6 |
| Deployment topology | **RATIFIED** — modular monolith, containers, managed Postgres; no K8s without measured need | `G0_B9_DEPLOYMENT_STRATEGY.md` |
| Clean repo structure | **RATIFIED** — `apps/platform/agents/sectors/schemas/config/migrations` | `G0_B9_REPOSITORY_STRUCTURE.md` |
| Secret management | **PROVISIONAL_G1_VALIDATE** — store-backed resolver at G1.10; DEV_RUNTIME_ONLY today | `G0_B9_SECRET_MANAGEMENT_PLAN.md` |
| Humanizer | **RATIFIED (bounded)** — disposition REVISE; subordinate to Book 7 promotion | Amendment 003 + Book 7 record |
| Model providers | **RATIFIED** — replaceable adapters behind the gateway | `G0_B9_DEPENDENCY_MANIFEST.md` |
| Compozy/QM substrates | **REJECTED at G0** (hard gate 7), **DEFERRED** for future re-profile | ADR + Batch 04 ledger |
| Automatic submission | **REJECTED permanently** — structurally impossible | constitution + migration test |

## Rule

Any future change to a RATIFIED decision requires a new ADR superseding
this one with explicit contradiction analysis (C29).
