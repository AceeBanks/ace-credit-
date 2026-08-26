# G0-B5-C23 — Failure & Degraded Modes

## Components

| Component | Role | Behavior when down |
|---|---|---|
| graph_projection | OPTIONAL | Core canonical state/decision recording continues; traversal degrades to explicit substrate |
| vector_store | OPTIONAL | Exact/relational/full-text retrieval continues; semantic retrieval disabled |
| semantica | OPTIONAL | System continues without losing canonical state; adapter reports unavailable |
| provenance_write | INTEGRITY_CRITICAL | Material decisions requiring provenance fail closed — no untraceable state |
| historical_evidence | INTEGRITY_CRITICAL | Replay marked integrity failure; reconstruction never fabricated |
| contradiction_service | INTEGRITY_CRITICAL | Conflicted facts never auto-promoted |

## Rules (DEG-001..003)

1. Optional component failure degrades only its own lanes; core canonical
   operation continues.
2. Integrity-critical failure fails closed: no untraceable production state,
   no fabricated reconstruction, no auto-promotion of conflicted facts.
3. Degraded mode decisions are recorded for audit (component, mode,
   fallback lane).

## Implementation

- `config/g0/evidence/degraded_modes.yaml`
- `prototype/g0/evidence/degradation.py` (`DegradationManager`)
- `tools/g0/validate_degraded_modes.py`
- `tests/g0/book5/test_degraded_modes.py`
