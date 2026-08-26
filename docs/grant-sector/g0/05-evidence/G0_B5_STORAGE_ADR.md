# G0-B5-C14 — Storage Decision ADR (R0-ADR-B5-C14)

| Field | Value |
|---|---|
| Status | RATIFIED (Book 5 band C14-C18) |
| Chapter | B5.C14 |
| Consumes | `G0_B5_SEMANTICA_BAKEOFF_RESULTS.json`, `G0_B5_SEMANTICA_BAKEOFF_REPORT.md` (C13) |
| Decision | **Pattern A — Relational canonical + relational evidence/dependency tables** |
| Semantica verdict | ADOPT_OPTIONAL_ACCELERATOR (deferred — adapter frozen, no runtime install) |
| Supersedes | none |

## Candidate patterns (from the charter)

- **A — Relational canonical + relational evidence/dependency tables**:
  simplest operationally; all truth in governed relational tables.
- **B — Relational canonical + graph projection**: canonical in relational
  store, graph optimized for traversal.
- **C — Relational canonical + Semantica-managed projection/index**:
  only if the bake-off justifies it.
- **D — Event-oriented provenance ledger + relational materialization +
  optional graph**: strongest replay model, higher complexity.

## Hard gate

All candidates A-D satisfy the hard gate (tenant isolation, historical
replay, canonical-ID preservation, rebuild/exit, provenance integrity) at
the prototype level: the explicit substrate already enforces tenant scope
on edges (GRAPH-002), preserves canonical ids (PROJ-001), supports temporal
replay (W6) and rebuild (W7), and keeps provenance in the system of record.
The bake-off (C13) showed **no correctness advantage** for a graph/Semantica
candidate on any of the ten workloads.

## Decision criteria weighting (from the charter, unchanged)

| Criterion | Weight | A | B | C | D |
|---|---|---|---|---|---|
| Correctness / provenance fidelity | 20% | 5 | 5 | 5 | 5 |
| Replayability | 15% | 4 | 4 | 4 | 5 |
| Tenant/security isolation | 15% | 5 | 4 | 3 | 5 |
| Replaceability / exit | 10% | 5 | 4 | 2 | 4 |
| Operational simplicity | 10% | 5 | 3 | 1 | 3 |
| Query capability | 10% | 3 | 5 | 5 | 4 |
| Performance | 5% | 4 | 4 | 4 | 4 |
| Developer ergonomics | 5% | 5 | 3 | 2 | 3 |
| Observability | 5% | 4 | 3 | 2 | 4 |
| Cost | 5% | 5 | 3 | 2 | 4 |

**Weighted totals**: A = 4.55, B = 4.05, C = 3.30, D = 4.45.

## Rationale

1. **Pattern A wins on the weighted criteria** (4.55 vs D's 4.45). D's
   replay edge does not justify its operational complexity at this stage;
   the temporal replay contract (C7-C9) already delivers replay semantics
   over the relational substrate.
2. **The bake-off found no workload where a graph candidate outperforms the
   explicit substrate** (C13: 9/9 shared workloads correct on both, both
   sub-ms). Pattern C would buy operational cost without measured benefit.
3. **Graph/vector systems remain projections** (EVID-LAW-015, PROJ-003).
   Pattern B's role is preserved for when a real data-scale workload shows a
   need; Semantica stays a deferred optional accelerator, never canonical
   truth.

## Committed decisions

- Physical evidence substrate = relational canonical tables + relational
  evidence/dependency tables (prototype: `prototype/g0/evidence/*`).
- Graph/vector indexes are optional projections, rebuildable from canonical
  evidence (W7), never the system of record.
- Semantica: adapter contract frozen; **no runtime install**. Activation
  requires a new ADR with measured recall/latency benefit at real data scale.
- Ledger entry recorded in the external-component decision ledger (DEFER).
