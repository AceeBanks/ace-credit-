# G0 Book 5 — Vector Index Contract

**Chapter:** B5.C11

## Rules

- VEC-001 — vectors are derived indexes, never canonical truth;
- VEC-002 — every vector points back to a stable source/artifact/evidence ref;
- VEC-003 — embedding model/version is recorded;
- VEC-004 — re-embedding does not change source identity;
- VEC-005 — deleted/restricted tenant content is removed/hidden per retention;
- VEC-006 — no cross-tenant similarity search by default;
- VEC-007 — vector metadata includes visibility and evidence class;
- VEC-008 — the index rebuilds from canonical artifacts/snapshots.

## Tests

`tests/g0/book5/test_graph_projection.py` (vector half) — full-loss recovery,
model swap preserves domain IDs, deletion hides from retrieval, cross-tenant
isolation default.
