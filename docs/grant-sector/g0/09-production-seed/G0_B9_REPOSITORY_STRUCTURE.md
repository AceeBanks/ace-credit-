# G0 Book 9 — Clean Repository Structure

**Chapter:** B9.C10
**Date:** 2026-08-27
**Status:** FROZEN

## Layout

```text
apps/
  api/          # REST facade, request scope resolution
  web/          # client-facing UI (G1.9)

platform/
  auth/         # identity, tenants, principals, sessions
  policy/       # capability registry, grant authority, approvals
  runtime/      # durable execution foundation (tasks, checkpoints, jobs)
  model/        # governed model gateway + provider adapters
  tools/        # independent tool gateway
  evidence/     # DecisionRecords, evidence lineage, audit
  evaluation/   # Book 7 evaluation, promotion, shadow/canary
  artifacts/    # versioned artifact service
  observability/# metrics, logs, traces, SLO

agents/
  personal_hermes/
  ceo_hermes/
  workers/
  contracts/    # IntentContract, TaskContract, WorkerResult, ContextBundle

sectors/
  grants/
    domain/        # Organization, Opportunity, OpportunityRevision,
                   # ApplicationProject, Requirements
    sources/       # adapters, SourceSnapshots, revision watcher
    eligibility/   # rule extraction + deterministic evaluation
    matching/      # ranking (never overrides eligibility)
    research/      # funder/winner/community evidence
    applications/  # blueprint, drafting orchestration
    budgets/
    qa/            # claim ledger, deterministic QA gates

schemas/       # JSON schemas for every contract
config/        # environment-aware config (secrets separated)
migrations/    # Postgres migrations (empty-DB reproducible)
tests/
evals/         # Book 7 golden sets, eval corpus
infra/         # containers, deployment, CI definitions
docs/
```

## Hard rules

1. **No trading directories.** OCE trading baggage stays out of the Grant
   repo (Amendment 002 / C10 hard rule).
2. **Ownership boundaries follow `G0_B9_PRODUCTION_SERVICE_TOPOLOGY.md`** —
   each directory maps to exactly one owner module.
3. **Contracts live once**: `agents/contracts/` + `schemas/` are the single
   source; implementation imports them, never redefines.
4. **Canonical tables are created only by `migrations/`**; application code
   never DDLs.
5. **Secrets are never in `config/`** — only references to the secret store
   (C21).

## Lineage

Every seeded item carries a `seed_item_id` with source lineage
(`G0_B9_SEED_MANIFEST.json`) — source type (`NEW | SALVAGED |
EXTERNAL_WRAPPED`), source repo/path/commit, license, modifications, owner
module, reason, tests.
