# G0 Book 9 — Observability & SLO Baseline

**Chapters:** B9.C18 + B9.C19
**Date:** 2026-08-27
**Status:** FROZEN (baseline; production collector is G1.10)

## Correlation model

One correlation id spans:
`user request → intent → task → worker → model request → ModelResponse →
DecisionRecord → artifact → audit`.

Every SliceRecord, DecisionRecord, model audit ref, and artifact ref in G0
already carries the id chain needed to join this trace.

## Metrics baseline (from Book 8 telemetry)

### Application/runtime
| Metric | Source |
|---|---|
| request/task counts | slice stage records |
| success/failure | run outcomes |
| retries | drafting bounded retry |
| task age / checkpoint recovery | telemetry checkpoint_count, reconstruction time |

### Agent
| Metric | Source |
|---|---|
| model calls | ModelGateway audit |
| tokens (in/out) | ModelResponse (measured: 721 in / 486 out per D2 call) |
| latency | ModelResponse latency_ms (measured: ~7.0 s p50 single call) |
| cost | cost_usd_if_known |
| structured-output failures | gateway failures |
| context size | ContextBundle length |
| worker fanout | slice plan task count |

### Data/source
| Metric | Source |
|---|---|
| adapter health | source ingestion |
| snapshot freshness | source_snapshots.fetched_at |
| parser failures | Book 5 parser lanes |
| revision changes | opportunity_revisions count |

### Quality
| Metric | Source |
|---|---|
| unsupported claim rate | claim ledger (measured: 0 in live D2) |
| QA failure rate | deterministic suite |
| eval regression | Book 7 eval runs |
| human edit burden | NOT_PERFORMED recorded honestly |

### Security
| Metric | Source |
|---|---|
| denied capabilities | Authorizer reason codes |
| approval requests | ApprovalRegistry |
| suspicious egress | egress policy denials |
| auth failures | identity layer |
| cross-tenant attempts | scope denials (6/6 measured) |

## SLO baseline (initial, honest)

Derived from Book 8 measurements; integrity properties may exceed
latency targets. These are initial baselines to validate in G1, not
marketing numbers.

| SLO | Target | Basis |
|---|---|---|
| API availability | 99.5% monthly | standard for 1-region; validate in G1 |
| Accepted-task durability | 100% (no accepted task lost) | Book 8 invariant — task persisted before ack |
| Task recovery after restart | < 1 s for slice-scale state | measured 1.1 ms per 10 records |
| Source adapter freshness | within 24 h for tracked sources | G1 source watcher |
| Critical audit write success | 100% (audit before consequential state) | Book 5 law |
| Artifact generation success | 99% | artifacts versioned, immutable |
| Authorization service availability | 99.9% (fail closed) | deny-by-default makes unavailability a deny, not a breach |
| Backup recovery objective | RPO ≤ 24 h, RTO ≤ 4 h | Postgres nightly + WAL; validate restore quarterly |

> Rule: **Better to reject a write than create an unaudited consequential
> state.** Integrity > latency for all canonical writes.
