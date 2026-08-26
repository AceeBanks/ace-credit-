# G0-B5-C21 — Performance & Scale Envelope

## Purpose

Prevent a theoretically elegant evidence graph from becoming operationally
unusable.

## Methodology (explicit, reproducible)

- Fixtures: 1 tenant/10 opportunities (small), 10 tenants/1k opportunities
  (medium), 100 tenants/100k opportunities (synthetic, where practical).
- Workloads: exact provenance trace, contradiction lookup, dependency
  invalidation, evidence bundle assembly, replay packet assembly, graph
  traversal.
- Metrics: p50/p95 latency, memory, rebuild time, invalidation fanout.
- Run: `python tools/g0/validate_performance_envelope.py` (runs the
  small-fixture benchmark against the prototype ceilings).

## Prototype ceiling (measured baseline, not an invented SLA — PERF-001)

| Metric | Ceiling |
|---|---|
| p50 latency | 50 ms |
| p95 latency | 200 ms |
| graph traversal hops | 8 |

Deterministic lanes (exact provenance traces, contradiction lookup) must
never be replaced by semantic search (PERF-002). G1 sets production targets
from real data-scale measurements.

## Implementation

- `config/g0/evidence/performance_envelope.yaml`
- `prototype/g0/evidence/benchmarks.py`
- `tools/g0/validate_performance_envelope.py`
- `tests/g0/book5/test_performance_envelope.py`
