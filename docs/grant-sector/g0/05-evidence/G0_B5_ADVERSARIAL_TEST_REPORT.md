# G0 Book 5 — Adversarial Test Report

**Suite:** `tests/g0/book5/test_adversarial_evidence.py`
**Result:** **80 passed, 1 skipped, 0 failed** (live run, 2026-08-26)

## Coverage

All 40 catalog scenarios (`config/g0/evidence/adversarial_evidence.yaml`,
validated by `tools/g0/validate_adversarial_evidence.py`) are attacked
against the real prototypes. 38 scenarios are P0; all P0 scenarios pass.

| Cluster | Scenarios |
|---|---|
| Fabrication | ADV-01, ADV-04, ADV-21, ADV-22 |
| Substitution | ADV-03, ADV-06, ADV-07, ADV-23 |
| Leakage | ADV-11, ADV-12, ADV-13, ADV-30, ADV-38 |
| Escalation | ADV-09, ADV-31, ADV-32, ADV-19 |
| Stale-state shortcuts | ADV-16, ADV-26, ADV-33, ADV-36 |
| Integrity failures | ADV-27, ADV-34, ADV-37, ADV-40 |
| Optional-component degradation | ADV-24, ADV-25, ADV-05, ADV-10 |
| Policy/governance | ADV-02, ADV-08, ADV-14, ADV-15, ADV-17, ADV-18, ADV-20, ADV-28, ADV-29, ADV-35, ADV-39 |

## Guards hardened during this suite

- GRAPH-004 — self-loop SUPPORTS edges denied
- GRAPH-005 — CORROBORATES requires distinct source content
- FIND-006 — research evidence bottoms out at sources (no recursive self-citation)
- CLAIM-008 — statistic geography/unit must match the claim
- INV-008 — stale dependency results blocked until recompute
- CONTR-004 — resolved contradictions reopen on amendment
- VIS-007 — license-restricted reuse requires approval
- DEC-002 enforcement — deterministic replay requires engine metadata
- claim-ledger missing-vs-stale: fabricated refs are UNSUPPORTED, never
  merely STALE

## Integration & property suite (C25)

`tests/g0/book5/test_integration_properties.py` — **24 tests**: all 20
mandatory invariants plus property tests (deterministic replay, idempotent
invalidation, DecisionRecord serialization round-trip, independent
corroboration). 22 passed, 2 skipped (Semantica-dependent projection
rebuild tests, environment-scoped).
