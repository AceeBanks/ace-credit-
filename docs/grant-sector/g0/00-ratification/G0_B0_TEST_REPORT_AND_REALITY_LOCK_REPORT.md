# G0 Book 0 — Test Report & Reality Lock Report

**Test command:** `python -m pytest tests/g0/book0 -q`
**Result:** **50 passed, 0 failed, 0 blocked, 0 skipped** (as recorded in `G0_B0_REALITY_LOCK.json`)

## Coverage by chapter

| Suite | Tests | Proves |
|---|---|---|
| `test_artifact_manifest.py` | 7 | Manifest structural integrity; content-pin drift detection fails closed; supersession cycles fail; duplicate IDs fail |
| `test_decision_register.py` | 12 | Register soundness; every required category covered; no phantom lineage; conditions required for conditional ratifications; negative fixtures for all defect classes |
| `test_contradictions.py` | 10 | All ten mandated probes present; zero open P0 enforced by gate; OPEN P0 fixture fails validation; phantom sources/decisions fail |
| `test_freeze_registers.py` | 13 | All three non-goal kinds present; ten mandated candidates with baselines/kill criteria/licenses; premature ADOPTED status fails gate |
| `test_reality_lock.py` | 8 | Lock is DERIVED: open P0, missing category, stale authority, premature adoption, failing or missing tests each flip readiness to FAIL |

## Adversarial design notes

- Every validator was proven against injected defects (negative fixtures), not just
  the happy path — a validator that cannot fail cannot prove anything.
- The Reality Lock treats a not-run test suite as blocking (`book0_tests_all_pass: null`
  ⇒ FAIL), so absence of evidence never reads as success.
- Readiness is a conjunction of predicates computed from five validators plus a live
  pytest run; no predicate is hand-written.

## Reality Lock reproduction

```bash
python tools/g0/build_book0_reality_lock.py \
  --out docs/grant-sector/g0/00-ratification/G0_B0_REALITY_LOCK.json
```

Exit code 0 ⇔ PASS. Regeneration is deterministic given repository state.
