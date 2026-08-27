# G0 Book 9 — Production Service Topology

**Chapter:** B9.C8
**Date:** 2026-08-27
**Status:** FROZEN

## Principle

> Start **modular monolith / few services**. Preserve internal module
> boundaries so extraction later is possible. Do not split into
> microservices merely to appear enterprise-grade.

Book 8 evidence shows a single-process Python slice with 10 durable stage
records per grant package and ~4 model calls — nowhere near microservice
scale. The topology below is the **logical** module map; physical
deployment starts as a small number of containers (C16).

## Logical modules

| Module | Owner | Data ownership | Input contracts | Failure mode | Auth boundary | Scaling trigger |
|---|---|---|---|---|---|---|
| API / app backend | product | none (facade) | REST intents, projects, drafts | degraded UX | user session → tenant scope | API volume |
| Personal Hermes | product | Hermes memory (curated) | client conversation → IntentContract | graceful: holds, no auto-answer | user → tenant | client count |
| CEO Hermes | product | Hermes memory (curated) | IntentContract → TaskPlan | fails closed on ambiguity | user/CEO → tenant+project | project count |
| Worker runtime | platform | none (results only) | TaskContract → WorkerResult | task-scoped retry | worker principal → task scope | fanout |
| Policy/capability | platform | Postgres (policy tables) | authorize(principal, capability, scope) | deny-by-default | PDP internal | auth volume |
| Model gateway | platform | execution audit refs | ModelRequest → ModelResponse | provider failover | PDP-gated; egress-policy | model calls |
| Tool gateway | platform | none | PDP-verified tool calls | deny on forged decision | PDP-gated | tool calls |
| Source ingestion | sector | Postgres snapshots meta + object storage raw | source fetch → SourceSnapshot | quarantine bad source | service identity | source volume |
| Evidence/research | sector | Postgres evidence + object payloads | findings, evidence lineage | fail closed on unsupported | service identity + project scope | research volume |
| Application/drafting | sector | Postgres project + artifacts | blueprint → sections | QA hard gate blocks | worker task scope | drafts |
| Artifact service | sector | object storage | versioned artifacts | immutable versions | project scope | artifact volume |
| Evaluation | platform | Postgres eval results | CandidateChange → PromotionDecision | deterministic gates first | eval-only identity | eval runs |
| Scheduler/jobs | platform | Postgres job meta | refresh/invalidation jobs | retry + idempotent | service identity | job volume |
| Postgres | infra | **canonical** | — | failover/backup | network-isolated | data volume |
| Object storage | infra | **immutable payloads** | — | versioned | IAM-scoped | payload volume |
| Redis/queue (optional) | infra | transport only | — | loss tolerated | network-isolated | message volume |
| Graph/vector (optional) | infra | rebuildable projection | — | rebuild on loss | service identity | query volume |

## Deployment shape (initial)

- 1 API/backend container (module-monolith hosting Personal/CEO/workers/
  policy/gateways/ingestion/drafting/eval in-process, import-boundary
  separated)
- 1 worker container (same image, different entrypoint) if background jobs
  warrant separation
- Managed Postgres (or self-hosted with proven backup)
- Object storage (S3-compatible)
- Optional Redis for transport/rate-limits
- Model gateway inside backend; provider adapter registry replaceable

Extraction triggers (do NOT extract before): sustained API volume without
worker co-tenancy, source ingestion backpressure, model-gateway isolation
requirements, eval runs impacting latency.

## Auth boundaries

- API → tenant scope: user session resolves tenant; every request carries
  tenant+project.
- Personal Hermes → tenant scope; CEO → tenant+project; workers → the
  specific TaskContract scope only.
- Model/Tool gateways → PDP-issued AuthorizationDecision; no caller JSON.
- Background jobs → scoped service identity with least privilege.
