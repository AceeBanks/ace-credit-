# G0 Book 5 — Test Report

**Test command:** `python -m pytest tests/g0 -q`
**Result:** **1186 passed, 3 skipped, 0 failed** (full suite)
**Book 5 suite:** **228 passed, 3 skipped** across 21 files
(`python -m pytest tests/g0/book5 -q`)

## Full-suite breakdown

| Suite | Tests |
|---|---|
| Book 0 (`tests/g0/book0`) | 51 |
| Book 1 (`tests/g0/book1`) | 133 |
| Book 2 (`tests/g0/book2`) | 255 |
| Book 3 (`tests/g0/book3`) | 243 |
| Book 4 (`tests/g0/book4`) | 276 |
| Book 5 (`tests/g0/book5`) | 228 passed (+3 skipped) |
| **Total (`tests/g0`)** | **1186 passed, 3 skipped** |

## Book 5 coverage by chapter

| File | Tests | Chapters |
|---|---|---|
| `test_evidence_constitution.py` | 10 | C1 — evidence constitutional laws |
| `test_provenance_graph.py` | 10 | C2-C3 — provenance refs + graph semantics |
| `test_evidence_quality.py` | 7 | C4 — quality dimensions |
| `test_evidence_contradictions.py` | 11 | C5-C6 — promotion + contradiction retention |
| `test_decision_records.py` | 5 | C7 — DecisionRecord |
| `test_temporal_replay.py` | 5 | C8 — deterministic replay |
| `test_dependency_invalidation.py` | 6 | C9 — selective invalidation |
| `test_retrieval_authority.py` | 6 | C10 — retrieval lanes + authority gate |
| `test_graph_projection.py` | 9 | C11-C12 — vector/graph projection contracts |
| `test_explanation_packet.py` | 5 | C15 — ExplanationPacket |
| `test_claim_ledger.py` | 6 | C16 — Application Claim Ledger |
| `test_research_finding.py` | 5 | C17 — Research Finding model |
| `test_audit_linkage.py` | 5 | C18 — audit↔evidence↔decision linkage |
| `test_eval_lineage.py` | 5 | C19 — eval dataset lineage |
| `test_draft_readiness.py` | 5 | C20 — D0/D1 evidence readiness |
| `test_performance_envelope.py` | 4 | C21 — performance envelope |
| `test_visibility.py` | 4 | C22 — privacy + visibility |
| `test_degraded_modes.py` | 6 | C23 — failure/degraded modes |
| `test_adversarial_evidence.py` | 80 | C24 — ADV-01..40 adversarial suite |
| `test_integration_properties.py` | 24 | C25 — 20 invariants + property tests |
| `test_book5_reality_lock.py` | 13 | C26 — Reality Lock freshness/defect injection |
| **Total** | **231 collected (228 passed, 3 skipped)** | C1-C26 |

The 3 skipped tests require the scoped `.bakeoff/` Semantica dependency on
the import path (projection rebuild/exit properties); the same behavior is
proven by the committed bake-off artifact (`G0_B5_SEMANTICA_BAKEOFF_RESULTS.json`).

## Live run note

All totals above are from the live run on 2026-08-26
(`python -m pytest tests/g0 -q` → 1186 passed, 3 skipped; book 5 →
228 passed, 3 skipped). No totals are inferred or carried over from prior
runs.
