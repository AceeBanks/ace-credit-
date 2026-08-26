# G0 Book 5 — Dependency Invalidation Model

**Chapter:** B5.C9 · **Schemas:** `dependency_edge.schema.json`, `invalidation_event.schema.json` · **Config:** `config/g0/evidence/invalidation_rules.yaml`

## Selective behavior

| Change | Effect |
|---|---|
| deadline change (OpportunityRevision) | eligibility timing → requirement deadline → readiness → user alert |
| community statistic update | affected proposal sections / research report |
| formatting-only change | no semantic invalidation if normalized meaning unchanged |

## Hard rules

- INV-004 — no global recompute when the dependency subset is known;
- INV-005 — transitive invalidation is bounded and inspectable;
- INV-006 — cycles are handled safely (no invalidation storm);
- INV-007 — a stale dependency prevents false submission-ready state.

## Tests

`tests/g0/book5/test_dependency_invalidation.py` — 6 tests (selective
invalidation, nonmaterial no-op, bounded transitivity, cycle safety, unknown
type rejection, stale-blocks-readiness).
