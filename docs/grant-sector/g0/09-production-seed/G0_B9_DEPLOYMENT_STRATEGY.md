# G0 Book 9 — Deployment Strategy

**Chapter:** B9.C16
**Date:** 2026-08-27
**Status:** FROZEN

## Principle

Cloud is deployment, not the architectural source of truth. Do not choose
Kubernetes unless measured evidence justifies it (Book 8 evidence does
not). Keep provider portability where practical.

## Initial preferred shape

- **Containerized services** — backend (modular monolith) + worker image
  (same image, different entrypoint).
- **Managed Postgres or self-hosted equivalent** with proven backup
  (nightly + WAL/PITR where available).
- **Managed/simple object storage** (S3-compatible).
- **Lightweight runtime deployment** — single-node containers first;
  horizontal worker scaling only where measured (Book 8 evidence: ~4 model
  calls and 10 records per grant package → single worker instance is
  ample at G0/G1 start).
- **Optional Redis** for transport/rate-limits if a need appears.

## Decisions

| Item | Decision |
|---|---|
| Regions | single region initially; configurable |
| Network boundaries | private VPC subnet for DB; public ingress only at API (TLS) |
| TLS | terminate at load balancer; internal traffic over TLS/mTLS where available |
| Database connectivity | private network; no public DB port |
| Worker execution isolation | task-scoped worker principals; container-per-service; no privileged access |
| Secret injection | environment injection from secret store at deploy (C21); never baked into image |
| Rolling deployments | blue/green or rolling with health checks; no downtime for API |
| Migration ordering | migrate-before-deploy; release records migration version + rollback target |
| Rollback | deploy previous immutable build artifact; DB rollback per migration policy |

## Anti-decisions (explicit)

- No Kubernetes/service mesh at G0/G1 start — no measured evidence of need.
- No multi-region at G0/G1 start.
- No vendor-locked PaaS abstractions that block the portable DDL/object
  storage path.

## Release identity

Every production release identifies: commit, version tag, build artifact,
migration version, rollback target (`G0_B9_CI_CD_POLICY.md`).
