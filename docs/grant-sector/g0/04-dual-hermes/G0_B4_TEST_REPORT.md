# G0 Book 4 — Test Report

**Test command:** `python -m pytest tests/g0 -q`
**Result:** **958 passed, 0 failed** (full suite)
**Book 4 suite:** **276 passed** across 19 files (`python -m pytest tests/g0/book4 -q`)

## Full-suite breakdown

| Suite | Tests |
|---|---|
| Book 0 (`tests/g0/book0`) | 51 |
| Book 1 (`tests/g0/book1`) | 133 |
| Book 2 (`tests/g0/book2`) | 255 |
| Book 3 (`tests/g0/book3`) | 243 |
| Book 4 (`tests/g0/book4`) | 276 |
| **Total (`tests/g0`)** | **958** |

## Book 4 coverage by chapter

| File | Tests | Chapters |
|---|---|---|
| `test_dual_hermes_boundary.py` | 16 | C1 — Dual-Hermes constitutional boundary |
| `test_role_contracts.py` | 16 | C2-C3 — Personal + CEO operating contracts |
| `test_intent_contract.py` | 14 | C4 — IntentContract |
| `test_clarification_flow.py` | 11 | C5 — Clarification/escalation protocol |
| `test_task_delegation.py` | 22 | C6-C7 — TaskPlan + TaskContract |
| `test_worker_sidechains.py` | 13 | C8-C9 — Sidechains + WorkerResult + synthesis |
| `test_context_boundaries.py` | 14 | C10-C11 — ClientExplanation + ContextBundle |
| `test_personal_memory.py` | 11 | C12 — Personal memory constitution |
| `test_ceo_memory.py` | 11 | C13 — CEO memory constitution |
| `test_memory_promotion.py` | 12 | C14-C15 — Worker memory + promotion |
| `test_memory_supersession.py` | 7 | C16 — Supersession/forgetting |
| `test_compaction.py` | 15 | C17 — Compaction + anchor/fact preservation |
| `test_reconstruction.py` | 8 | C19 — Cold-restart reconstruction |
| `test_feedback_loop.py` | 10 | C20-C21 — Co-adaptation + client feedback |
| `test_d1_mock_draft_flow.py` | 9 | C22 — D1 Hermes mock-draft contract |
| `test_portability_privacy.py` | 13 | C23-C25 — Skill boundaries + model independence + privacy |
| `test_adversarial_context_pollution.py` | 30 | C26 — Adversarial suite A1-A25 (+ catalog guards) |
| `test_integration_reconstruction.py` | 29 | C27 — 22 invariants + 5 property tests (+ guards) |
| `test_book4_reality_lock.py` | 15 | C28 — Reality Lock derivation + freshness |
| **Total** | **276** | |

## Validator CLIs (all PASS at BOOK time)

```bash
python tools/g0/validate_dual_hermes_boundary.py
python tools/g0/validate_role_contracts.py
python tools/g0/validate_intent_clarification.py
python tools/g0/validate_task_delegation.py
python tools/g0/validate_sidechain_synthesis.py
python tools/g0/validate_context_explanation.py
python tools/g0/validate_memory_constitutions.py
python tools/g0/validate_memory_lifecycle.py
python tools/g0/validate_compaction_reconstruction.py
python tools/g0/validate_feedback_loop.py
python tools/g0/validate_d1_contract.py
python tools/g0/validate_portability.py
python tools/g0/validate_adversarial_context.py
```

## Notes

- Book 4 tests are fail-closed: injected defects flip assertions to red; the
  Reality Lock freshness suite proves each injected defect flips readiness to
  FAIL and that the committed lock equals honest regeneration.
- The lock's inner derivation run records **275 passed + 1 skipped** (the
  lock-freshness self-test excludes itself via `G0_SKIP_LOCK_FRESHNESS=1`),
  plus a dedicated adversarial run of **30 passed**.
- All counts are from real runs (`python -m pytest`), never hand-written.
