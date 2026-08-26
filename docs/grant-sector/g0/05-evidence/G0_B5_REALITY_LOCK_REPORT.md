# G0 Book 5 — Reality Lock Report

**Lock:** `G0_B5_REALITY_LOCK.json` (derived, machine-readable)
**Builder:** `tools/g0/build_book5_reality_lock.py`
**Freshness suite:** `tests/g0/book5/test_book5_reality_lock.py` (13 tests)

## Status

```text
status: PASS
p0_open: 0
ready_for_book6: true
```

## Derived predicates (all true)

| Predicate | Derived from |
|---|---|
| evidence_constitution_complete | evidence constitution validator |
| provenance_model_pass | provenance/graph edge semantics validator |
| evidence_graph_semantics_pass | provenance validator + hard rules |
| decision_record_pass | decision types + invalidation rules validator |
| historical_replay_pass | configs AND green live test run |
| contradiction_retention_pass | quality + contradiction config validator |
| dependency_invalidation_pass | decision/invalidation configs AND green tests |
| retrieval_authority_pass | retrieval + projection policies validator |
| graph_rebuild_exit_pass | bake-off results: W7 rebuild correct |
| vector_rebuild_exit_pass | projection + visibility configs AND green tests |
| semantica_bakeoff_complete | `G0_B5_SEMANTICA_BAKEOFF_RESULTS.json` (both candidates ≥9/9) |
| storage_adr_ratified | `G0_B5_STORAGE_ADR.md` RATIFIED, Pattern A |
| tenant_isolation_pass | provenance + visibility configs AND green tests |
| claim_ledger_pass | claim ledger + research policy validators |
| client_explanation_pass | explanation policy validator |
| audit_evidence_linkage_pass | linkage policy validator |
| eval_lineage_pass | eval lineage policy validator |
| d0_d1_evidence_ready | draft readiness policy validator |
| adversarial_p0_pass | adversarial catalog validator AND green ADV/integration run |

## Freshness / defect-injection proof

The freshness suite proves the lock is derived, not hand-written: each
injected defect flips the lock to FAIL — broken evidence law, missing
GRAPH-002, unknown decision type, corrupted contradiction types, missing
bake-off results, unratified storage ADR, missing EVAL-005, broken EXPL-002,
failing book-5 tests, failing adversarial run, and no-test-run mode. The
committed lock must equal a fresh regeneration (stale-lock guard).

## Status wording

INTERNAL REALITY LOCK PASS. External ratification is performed separately
(see `G0_B5_HANDOFF_TO_BOOK_6.md`).
