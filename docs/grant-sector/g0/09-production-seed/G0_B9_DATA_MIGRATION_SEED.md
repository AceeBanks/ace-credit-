# G0 Book 9 — Data Migration Seed

**Chapter:** B9.C13
**Date:** 2026-08-27
**Status:** SEEDED + EMPTY-DB TESTED (sqlite); Postgres run in CI/staging

## Canonical tables seeded

| Table | Source contracts | Owner |
|---|---|---|
| `tenants` | Book 6 tenant scope | platform/auth |
| `users`, `principals` | Book 4/6 identity | platform/auth |
| `capabilities`, `grants` | Book 6 capability/grant registry | platform/policy |
| `approvals` | Book 6 ApprovalRegistry | platform/policy |
| `organizations` | Book 2/8 | sectors/grants/domain |
| `opportunities`, `opportunity_revisions` | Book 2 append-only revision chain | sectors/grants/domain |
| `application_projects` | Book 8 vertical slice | sectors/grants/domain |
| `requirements` | Book 2/8 | sectors/grants/domain |
| `source_snapshots` | Book 5 immutable snapshots | sectors/grants/sources |
| `decision_records` | Book 5 replayable decisions | platform/evidence |
| `audit_events` | Book 5/6 audit | platform/evidence |
| `artifacts` | Book 7 ArtifactVersion | platform/artifacts |
| `tasks` | Book 8 durable task foundation | platform/runtime |

## Migration rules

1. **Append-only.** Never edit an applied migration; new changes are new
   files (`002_*.sql`, …).
2. **Portable DDL.** TEXT primary keys (G0 string ids), no server-specific
   types — the same file runs from an EMPTY database in sqlite (dev/CI)
   and Postgres (staging/production).
3. **Empty-DB reproducible.** Verified by
   `production-seed/tests/test_migration_seed.py` (4 tests): schema builds,
   no submission capability, FK enforcement, seed rows round-trip.
4. **No local historical DB state** is required or referenced.

## Enforcement

- Application code never executes DDL; migrations are the only schema path.
- Postgres migration run is part of CI (staging job) and the release
  pipeline runs `migrate` before deploy with a recorded rollback target
  (`G0_B9_CI_CD_POLICY.md`).
- Graph/vector projections are rebuildable from these tables; they are not
  seeded here (non-sovereign).
