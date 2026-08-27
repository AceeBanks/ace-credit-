# G0 Book 9 — Book 8 Workload Evidence

**Chapter:** B9.C1
**Source:** Book 8 vertical slice telemetry (`prototype/g0/vslice/telemetry.py`),
live D2 model run (`D2_LIVE_BASELINE_MODEL_RUN.json`), Book 8 Reality Lock
builder probes, reconstruction measurements.
**Date:** 2026-08-27
**Note:** Every number below is tagged `MEASURED | DERIVED | ESTIMATED | UNKNOWN`.
One fixture does not equal enterprise scale; scaling is explicit in
`G0_B9_COST_ENVELOPE.md`.

## Workload characteristics

| Metric | Value | Basis |
|---|---|---|
| Concurrent application projects (single fixture run) | 1 | MEASURED |
| Vertical slice stages (durable records) | 10 (`intent, plan, selection, eligibility, match, research, project, drafting, assurance, package`) | MEASURED |
| Audit/evidence events per slice run | 10 (one durable `SliceRecord` per stage) | MEASURED |
| Task count per slice run | 7 | DERIVED (telemetry task_count) |
| Checkpoint count per slice run | 6 | DERIVED (telemetry checkpoint_count) |
| Worker fanout (planned delegation) | 4 (research, drafting, budget, QA lanes) | MEASURED (slice plan) |
| Worker fanout (model lanes) | 4 model calls per full live slice (one per blueprint section) | MEASURED (drafting module) |
| ContextBundle size (model drafting input) | ~250 tokens per section request | DERIVED (evidence string) |
| Model input tokens (single D2 baseline call) | 721 | MEASURED |
| Model output tokens (single D2 baseline call) | 486 | MEASURED |
| Model total tokens (single call) | 1,207 | MEASURED |
| Model latency p50 (single call) | 7.0 s (`latency_ms=7022.9`) | MEASURED |
| Model cost (single call) | $0 (free-tier router; NOT a production pricing basis) | MEASURED |
| Model retries | 0–1 (bounded retry on empty completion) | MEASURED (drafting module) |
| Cold-restart reconstruction time | ~1.1 ms for 10 records | MEASURED (reconstruction probe) |
| Source fetches per slice | 3 (fixture-bound: snapshot, revision, community stat refs) | MEASURED |
| Parser workload | 0 in live slice (fixture evidence is structured) | MEASURED — parser exercised only in Book 5 tests |
| Revision invalidation activity | 1 amendment drill: 6 downstream stages selectively invalidated on material change; 0 on non-material | MEASURED (amendment drill) |
| Approval interactions | 0 in current slice (no approval-gated ops exercised live); approval machinery tested in Book 6 | MEASURED |
| Security denials per attack suite | 6/6 attacks denied (cross-tenant, cross-project, provider bypass, credential extraction, submission, SSRF) | MEASURED (resilience module) |
| Tenant isolation | Single tenant exercised (`tenant-a`); cross-tenant denial verified | MEASURED |
| Project isolation | Single project (`proj-slice`); cross-project denial verified | MEASURED |
| Optional component failure | research/drafting degrade locally; eligibility failure fails closed | MEASURED (degraded-mode drill) |

## Derived per-tenant-per-grant estimates

| Metric | Value | Basis |
|---|---|---|
| Model calls per grant package | ~4 (drafting) + 1 (Humanizer, if used) | DERIVED |
| Model tokens per grant package | ~5,000 input + ~2,000 output (4 × ~1.2k) | DERIVED |
| Model latency per grant package | ~28 s (4 × ~7 s, sequential) | DERIVED |
| DB write volume per grant package | ~20 rows (10 stage records + decision refs + artifacts) | ESTIMATED |
| Audit events per grant package | ~15 (stage records + model audit + QA events) | ESTIMATED |

## Scaling envelope (explicit, not fake precision)

| Scenario | Concurrent clients | Grant packages/day | Model calls/day |
|---|---|---|---|
| DEV / single client | 1 | 1–2 | ~10 |
| 10 clients | 10 | 20 | ~100 |
| 100 clients | 100 | 200 | ~1,000 |

Model cost scenarios are configurable — see `G0_B9_COST_ENVELOPE.md`.
Free-tier model pricing is explicitly NOT a production cost basis.

## What this proves (and does not)

Proven: the architecture and grounding discipline — bounded workers,
governed model gateway, durable stage records, claim ledger, deterministic
gates, amendment selective-invalidation, cold restart, security denials.

Not proven: universal proposal quality, production-scale concurrency, real
parser/source-fetch workloads, approval-heavy flows, multi-tenant live
load. Those are G1 workloads with real adapters; runtime selection must not
assume more than this evidence supports.
