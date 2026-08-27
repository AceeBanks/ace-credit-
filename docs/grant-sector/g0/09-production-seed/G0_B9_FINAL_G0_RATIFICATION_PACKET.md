# G0 Book 9 — Final G0 Ratification Packet

**Date:** 2026-08-27
**Status:** G0 implementation complete; external ratification NOT
self-claimed by the build agent — this packet is the audit trail for a
human external reviewer.

## What G0 delivered

1. **Constitution** (Book 1) — deny-by-default authority, tenant/project
   isolation, server-side secrets, submission structurally disabled.
2. **Grant-domain kernel** (Book 2) — Opportunity/OpportunityRevision,
   deterministic eligibility.
3. **Governed source ingestion** (Book 3) — immutable SourceSnapshots,
   Georgia-first fixtures.
4. **Dual Hermes + bounded workers** (Book 4) — IntentContract, TaskPlan,
   TaskContract, WorkerResult, ContextBundle.
5. **Evidence + replay** (Book 5) — DecisionRecords, evidence lineage.
6. **Security** (Book 6) — Authorizer, ToolGateway, ApprovalRegistry,
   DecisionRegistry, project scope; 1,778-test suite.
7. **Evaluation + promotion** (Book 7) — quality taxonomy, deterministic-
   first gates, single promotion path, live D2 experiment + Humanizer
   bake-off (disposition REVISE).
8. **Vertical slice** (Book 8) — full production-shaped Georgia slice,
   live model drafting, amendment drill, cold restart, degraded mode,
   security attacks, telemetry.
9. **Book 9** — workload evidence, runtime requirements, candidate
   profiles + hard gates, bake-off, **ADR: OCE_NATIVE**, canonical
   ownership, service topology, interfaces, clean repo seed, dependencies/
   licenses, migrations (empty-DB tested), environments, deployment, CI,
   observability/SLO, recovery, secrets, security, cost, fresh-clone
   verification, G1 backlog, architecture freeze, contradiction sweep,
   reconstruction guide, final Reality Lock.

## Key artifacts

| Artifact | Path |
|---|---|
| Runtime ADR | `docs/grant-sector/g0/09-production-seed/G0_B9_RUNTIME_SUBSTRATE_ADR.md` |
| Canonical ownership | `.../G0_B9_CANONICAL_STATE_OWNERSHIP.md` |
| G1 backlog | `.../G0_B9_G1_IMPLEMENTATION_BACKLOG.md` |
| Final Reality Lock | `docs/grant-sector/g0/00-ratification/G0_FINAL_REALITY_LOCK.json` |
| Clean seed | `production-seed/` |
| External reviews | `G0_B6_EXTERNAL_REVIEW_01.md`, `G0_B7_EXTERNAL_REVIEW_01.md`, `G0_B8_EXTERNAL_REVIEW_01.md` |

## Test totals

| Suite | Result | Classification |
|---|---|---|
| Full G0 (`tests/g0`) | **1812 passed, 3 skipped** | current_final_head at `84ebd8b9` |
| Full G0 at Book 8 seal | 1778 passed, 3 skipped | historical_at_sha `72a9082a` |
| Book 9 tests | 34 passed | current_final_head |
| Production seed tests | 4 (empty DB) | current_final_head |
| Fresh-clone bootstrap | PASS | current_final_head |

## Book counting semantics

- **Book 0** = foundation / pre-ratification book (not a ratified
  implementation Book).
- **Books 1–9** = nine ratified implementation Books, each with its own
  Reality Lock.

Therefore `books_ratified=9` (Books 1–9) is consistent with "G0 spans
Books 0–9" (ten books including the foundation Book 0).

## Reviewer checklist (external, not performed by the build agent)

- [ ] Ratify Book 7 evaluation methodology + live D2 draft + Humanizer
      disposition (REVISE).
- [ ] Ratify Book 8 vertical slice + Reality Lock.
- [ ] Ratify Book 9 ADR (OCE_NATIVE) + ownership + G1 backlog.
- [ ] Ratify G0 final Reality Lock (`ready_for_g1=true`).

## Open items (P1/P2, no P0)

- P1: writing-quality evidence is small-sample (single fixture/revision/
  model) — more Book 7 eval runs before promotion decisions.
- P1: production durable-execution (task table, queue, scheduler) is G1.1
  work (record-level durability measured in G0).
- P2: Postgres migration live-run is CI/staging exercise; local uses
  sqlite (same portable DDL).
- P2: clean repository creation is
  `CLEAN_REPO_CREATION_PENDING_OPERATOR_ACTION`.
