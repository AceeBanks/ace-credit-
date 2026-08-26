# G0 Book 5 — Evidence Graph Semantics

**Chapter:** B5.C3 · **Config:** `config/g0/evidence/evidence_edge_types.yaml`
· **Schema:** `schemas/g0/evidence/evidence_edge.schema.json`

## Meaning before technology

The graph is a semantic relationship model first; physical graph storage is
optional (EVID-LAW-015). Nodes are projections/references to Book 2/3/4
objects — never duplicate sovereign entities.

## Edge families

| Family | Edge types |
|---|---|
| Source lineage | EXTRACTED_FROM, NORMALIZED_FROM, OBSERVED_IN, DERIVED_FROM |
| Evidence semantics | SUPPORTS, CONTRADICTS, CORROBORATES, SUPERSEDES, QUALIFIES, MEASURES |
| Decision lineage | DECISION_USED, DECISION_PRODUCED, EVALUATED_AGAINST, EXPLAINED_BY |
| Application lineage | REQUIREMENT_SATISFIED_BY, ARTIFACT_USES, BUDGET_SUPPORTS, QA_CHECKED, REVIEWED_BY |
| Dependency semantics | DEPENDS_ON, INVALIDATES, REQUIRES_RECOMPUTE |

## Edge contract

```yaml
edge_id, edge_type, from_ref, to_ref, tenant_scope, created_at, created_by,
method, confidence_dimensions, valid_from, valid_to, status
```

## Hard rules

- **GRAPH-001** — edges cannot create facts that do not exist in the governed
  domain/evidence layer (endpoint compatibility enforced from config);
- **GRAPH-002** — cross-tenant edges are denied;
- **GRAPH-003** — tombstoning does not silently orphan historical replay.

## Tests

`tests/g0/book5/test_provenance_graph.py` — endpoint rules, cross-tenant
denial, unknown-type rejection, tombstone history, support-chain traversal
(W1 workload primitive).
