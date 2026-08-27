# G1 Wave 1 — Durable Platform Kernel (G1.1 + G1.2)

**Status:** COMPLETE (integration checkpoint passed)
**Commit plan:** G1-W1-C1 (repositories) → G1-W1-C2 (tasks) →
G1-W1-C3 (scheduler) → G1-W1-C4 (object storage) → G1-W1-BOOK.

## What was built

| Component | Classification | Location |
|---|---|---|
| Domain records (promoted from G0, JSON-serializable) | PROMOTE_FROM_G0 | `grant_platform/domain/records.py` |
| Durable Store (SQLite dev/CI — TEST_ONLY / DEV_FAST_PATH per P1-01; canonical Postgres migration path in `migrations/postgres/`, tenant-scoped) | HARDEN_FROM_G0 | `grant_platform/store/db.py` |
| Durable task/run system (claim, checkpoint, resume, retry, idempotency, lease/STALE recovery) | REIMPLEMENT_PRODUCTION | `grant_platform/runtime/tasks.py` |
| Postgres-backed job queue / scheduler | NEW | `grant_platform/runtime/scheduler.py` |
| Object storage abstraction (local fs now, S3 interface) | NEW | `grant_platform/store/objects.py` |

## Wave 1 test coverage (36 seed tests, all pass)

- empty-DB migration → lifecycle (tenant → org → opportunity → revision →
  project);
- append-only revision chain;
- cross-tenant isolation (scoped reads; tenant cannot read another
  tenant's rows);
- DecisionRecord + audit persistence;
- task claim → run → complete → reconstruct;
- simulated process death → lease expiry → STALE → recover → resume with a
  new worker;
- concurrent claim: only one worker wins;
- idempotent completion (never re-executes);
- bounded retry then FAIL;
- task tenant-scoping;
- object store roundtrip, content-addressing, traversal rejection;
- scheduler enqueue/dispatch/idempotency/retry/tenant scope.

## Constitutional invariants preserved

- Workflow truth in the Store (Postgres in production), never only Hermes
  memory;
- tenant/project scope structural;
- submission absent from the schema (migration test asserts);
- capability + grant records persisted for the G0 Authorizer integration.

## Remaining (honest)

- Postgres repository adapter (SQLAlchemy/psycopg) over the canonical
  production migration path `migrations/postgres/` (G1.2 completion).
  The P1-01 migration-truth repair established `migrations/postgres/`
  (TIMESTAMPTZ/`now()`/jsonb) as the production path and relabeled the
  SQLite schema as TEST_ONLY / DEV_FAST_PATH — SQLite is not evidence of
  Postgres correctness. `tests/test_postgres_migration.py` runs the real
  PG integration when `PG_TEST_DSN` is reachable and reports
  `BLOCKED_ENVIRONMENT` otherwise.
- Live concurrent multi-worker lease contention beyond single-process
  sqlite is exercised at staging.
