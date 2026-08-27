# G0 Book 9 — G1 Implementation Backlog

**Chapters:** B9.C26 + B9.C27
**Date:** 2026-08-27
**Status:** COMPLETE
**Rule:** G1 productionizes the G0 kernel — it does not rebuild working
code unnecessarily. Every component is classified
`PROMOTE_FROM_G0 | HARDEN_FROM_G0 | REIMPLEMENT_PRODUCTION | NEW`.

## Classification legend

- **PROMOTE_FROM_G0** — working, tested, move into the clean repo with
  minor wiring.
- **HARDEN_FROM_G0** — working prototype; needs production hardening
  (persistence, observability, config, scale).
- **REIMPLEMENT_PRODUCTION** — prototype pattern proved but the production
  form must be rebuilt on the selected substrate (Postgres/object storage/
  durable tasks).
- **NEW** — not present in G0; build in G1.

## G1 epics

### G1.1 Platform kernel — identity, tenants, policy, task/run foundation

| Item | Classification | Source |
|---|---|---|
| Tenants/principals/roles | PROMOTE_FROM_G0 | `prototype/g0/security/identity.py`, migrations seed |
| Deny-by-default Authorizer + grant authority ladder | PROMOTE_FROM_G0 | `prototype/g0/security/authorization.py` |
| Capability registry + grants | PROMOTE_FROM_G0 | `config/g0/security/capability_grant_policy.yaml` |
| ApprovalRegistry | PROMOTE_FROM_G0 | Book 6 repair |
| DecisionRegistry + AuthorizationDecision | PROMOTE_FROM_G0 | `prototype/g0/security/` |
| ToolGateway (PDP-verified) | PROMOTE_FROM_G0 | `prototype/g0/security/tool_gateway.py` |
| Production task table + checkpoint/resume | **REIMPLEMENT_PRODUCTION** | migrations `tasks` table; G0 record-level durability → durable task runner |
| Queue/scheduler for background jobs | **NEW** | source refresh, revision watcher |

### G1.2 Grant domain persistence

| Item | Classification | Source |
|---|---|---|
| Organization model | PROMOTE_FROM_G0 | `prototype/g0/domain/` + fixture |
| Opportunity + OpportunityRevision (append-only) | PROMOTE_FROM_G0 | `prototype/g0/domain/revisions.py` |
| ApplicationProject shell | PROMOTE_FROM_G0 | `prototype/g0/vslice/project.py` |
| Postgres repository layer | **NEW** | migrations seed; SQLAlchemy/psycopg adapters |
| Object-storage artifact refs | **NEW** | S3-compatible adapter |

### G1.3 Source ingestion

| Item | Classification | Source |
|---|---|---|
| SourceSnapshot identity (immutable, content-addressed) | PROMOTE_FROM_G0 | `prototype/g0/source/`, migrations `source_snapshots` |
| Georgia-first fixture adapter | PROMOTE_FROM_G0 | `prototype/g0/domain/fixtures/georgia.py` |
| Grants.gov/Simpler adapter | **NEW** | real source adapters (G0 used fixtures) |
| Revision watcher (source amendment → OpportunityRevision) | HARDEN_FROM_G0 | Book 8 amendment drill → scheduled adapter |
| Parser stack (PDF/doc → structured) | HARDEN_FROM_G0 | Book 5 parser lanes; production parser TBD |

### G1.4 Eligibility / matching

| Item | Classification | Source |
|---|---|---|
| Deterministic eligibility engine | PROMOTE_FROM_G0 | `prototype/g0/domain/eligibility.py` |
| Candidate rule extraction from solicitation | HARDEN_FROM_G0 | Book 2 interpretation |
| Match dimensions (never overrides eligibility) | PROMOTE_FROM_G0 | `prototype/g0/vslice/qualify.py` |

### G1.5 Research / evidence

| Item | Classification | Source |
|---|---|---|
| DecisionRecord + evidence lineage | PROMOTE_FROM_G0 | `prototype/g0/evidence/decisions.py` |
| Evidence refs → canonical facts/statistics | PROMOTE_FROM_G0 | Book 5 |
| Funder/winner/community adapters (USAspending etc.) | **NEW** | real data adapters |
| Graph/vector projections | **NEW** | rebuildable, non-sovereign |

### G1.6 Personal / CEO Hermes

| Item | Classification | Source |
|---|---|---|
| Personal Hermes (intent capture, IntentContract) | PROMOTE_FROM_G0 | `prototype/g0/agents/intent_builder.py` |
| CEO Hermes (decomposition, TaskPlan) | PROMOTE_FROM_G0 | `prototype/g0/agents/task_builder.py`, `vslice/planning.py` |
| Bounded workers + WorkerResult | PROMOTE_FROM_G0 | `prototype/g0/vslice/drafting.py` |
| Hermes execution adapter | **REIMPLEMENT_PRODUCTION** | production runtime execution (OCI-native) |
| Context assembly (ContextBundle) | PROMOTE_FROM_G0 | Book 4 contracts |

### G1.7 Application drafting

| Item | Classification | Source |
|---|---|---|
| Blueprint + requirements | PROMOTE_FROM_G0 | `prototype/g0/vslice/project.py` |
| Governed Model Gateway + provider adapters | HARDEN_FROM_G0 | `prototype/g0/model/gateway.py` — production secret resolver, provider pinning |
| Section drafting (live + deterministic lanes) | PROMOTE_FROM_G0 | `prototype/g0/vslice/drafting.py` |
| Budget reconciliation | PROMOTE_FROM_G0 | Book 8 |
| Artifact versioning | HARDEN_FROM_G0 | object storage backing |

### G1.8 QA / evaluation

| Item | Classification | Source |
|---|---|---|
| Claim Ledger + support metrics | PROMOTE_FROM_G0 | `prototype/g0/vslice/assurance.py` |
| Deterministic QA gates (8-gate) | PROMOTE_FROM_G0 | Book 7 assertions |
| Book 7 evaluation + promotion | PROMOTE_FROM_G0 | `prototype/g0/evaluation/` |
| Humanizer lane (bounded, disposition REVISE) | HARDEN_FROM_G0 | only per Book 7 promotion rules |

### G1.9 Client-facing product

| Item | Classification | Source |
|---|---|---|
| API endpoints (contract map) | **NEW** | `apps/api/` |
| Web client (intake, shortlist, draft review) | **NEW** | `apps/web/` |
| ExplanationPacket to client | PROMOTE_FROM_G0 | `prototype/g0/vslice/package.py` |

### G1.10 Operations hardening

| Item | Classification | Source |
|---|---|---|
| Observability collector + tracing | **NEW** | metrics baseline (C18) |
| Production secret store resolver | **REIMPLEMENT_PRODUCTION** | replaces DEV_RUNTIME_ONLY resolver |
| Backup/recovery drills | **NEW** | C20 |
| Security re-verification in production topology | **NEW** | C22 re-run |
| Cost telemetry | **NEW** | C23 configurable scenarios |

## Priority rules (B9.C27)

1. Correctness foundations (G1.1 kernel, G1.2 persistence).
2. Client-visible vertical slice (G1.6→G1.7→G1.8→G1.9) as soon as core
   contracts safely allow.
3. Reliability/security (G1.10).
4. Throughput/cost optimization.
5. Secondary integrations (source breadth, 50-state) on demand.
6. Later automation.

Do NOT prioritize: exotic multi-agent behavior, self-modification, huge
plugin ecosystems, 50-state coverage before demand, automatic submission,
speculative scale infrastructure.
