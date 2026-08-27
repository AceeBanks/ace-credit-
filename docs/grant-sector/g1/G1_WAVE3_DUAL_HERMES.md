# G1 Wave 3 — Production Dual Hermes Runtime

**Line:** `grant-sector-g1-production`
**Status:** IMPLEMENTED (SQLite dev/CI store is TEST_ONLY / DEV_FAST_PATH per P1-01; canonical Postgres migration path `migrations/postgres/`; repository adapter follows)
**Commit series:** `G1-W3-C1` … `G1-W3-BOOK`

## Constitutional Invariant

**Personal Hermes ≠ CEO Hermes ≠ Workers** (G0 §3).

| Owner | Owns | Does NOT do |
|---|---|---|
| **Personal Hermes** (`agents/personal.py`) | conversations, messages, intent extraction, clarification, client explanations | execute operational tools |
| **CEO Hermes** (`agents/ceo.py`) | TaskPlans, durable tasks, worker orchestration, synthesis | read raw transcripts, hold workflow truth in memory |
| **Workers** (`agents/workers.py`) | one task at a time, bounded ContextBundle, WorkerResult | persistent state, global context, model scratchpads |

## What Was Implemented

### Migration 002 — Hermes runtime tables (append-only)

`conversations`, `messages`, `intents` (IntentContract payloads),
`task_plans`, `worker_results`. All tenant-scoped; workflow truth lives in
the Store, never in Hermes memory (Book 8 reconstruction law).
`Store.migrate()` now applies all `migrations/*.sql` in order; the
empty-DB migration test now covers the new tables.

### Personal Hermes (`agents/personal.py`)

- `receive_message()` persists the client message, deterministically
  classifies intent type (never a model call — structural field, Book 8
  C34 deterministic-first), derives the bounded authority scope, and
  persists the IntentContract in `intents`.
- **Submission fail-closed:** `submission.*` / `application.submit`
  capability requests normalize to `application.prepare_submission_package`
  with an explicit normalization note. Personal never executes tools.
- Reply is persisted as a `personal_hermes` message — chat is a durable
  record, not the source of Grant truth.

### CEO Hermes (`agents/ceo.py`)

- `plan()` consumes the governed IntentContract (never the transcript),
  builds a TaskPlan anchored to the exact OpportunityRevision
  (`opp_rev_ga_501_1` by default), persists the plan, and enqueues durable
  `READY` tasks for delegable steps only.
- CEO-owned capabilities (`application.create_draft_project`,
  `application.prepare_submission_package`, `match.explain`) are never
  delegated. A CEO process crash loses nothing: all plan/task state is in
  the Store.
- `synthesize()` reads only the Store.

### Worker runtime (`agents/workers.py`)

- `run()` atomically claims a durable task (Wave 1 `TaskRunner`), assembles
  a **bounded ContextBundle** (`ctx:intent-*`, `ctx:rev-*` refs — no
  conversation refs), invokes a registered governed handler, writes a
  `WorkerResult` with material claims, and completes the task with a result
  ref.
- `build_bundle()` provably excludes raw conversation refs (tested).

### Cold reconstruction (`agents/reconstruction.py`)

- `reconstruct()` rebuilds organization / intent / project / revision /
  plan / tasks / worker results / decisions / artifacts purely from durable
  rows. `raw_chat_required` is structurally `False` (tested).

## Tests

`tests/test_dual_hermes.py` — 7 tests:

1. client message → persistent IntentContract (durable, both messages saved)
2. submission capability normalized fail-closed + CEO rejects poisoned intent
3. CEO durable plan → worker claim/execution → synthesis (reads Store only)
4. worker bundle never contains raw transcript refs
5. cold reconstruction with a simulated process death (new runtime instance)
6. cross-tenant isolation (tenant-a cannot see/read tenant-b rows)
7. concurrent task claim → exactly one winner

**Seed suite at Wave 3:** 52 passed, 0 failed. Fresh-clone verification PASS.

## Honest Status

- Store is SQLite-backed for dev/CI only (TEST_ONLY / DEV_FAST_PATH —
  P1-01 migration-truth repair; SQLite is not Postgres evidence). The
  canonical production migrations are `migrations/postgres/`
  (TIMESTAMPTZ/`now()`/jsonb), exercised by
  `tests/test_postgres_migration.py` (`BLOCKED_ENVIRONMENT` without a
  reachable server, never fake PASS). The Postgres repository adapter
  remains the G1.1 hardening item (same table layout, same repository
  interface).
- Worker drafting tasks are wired to handlers here; the governed Model
  Gateway call for `application.draft_section` lands in Wave 4.
