# G0 Book 3 — Adversarial Test Report

**Command:** `python -m pytest tests/g0/book3/test_adversarial_data.py -q`
**Result:** **26 passed, 0 failed** (A1-A25 plus the scenario-catalog validator test)

Config of truth: `config/g0/source/adversarial_data.yaml` (all 25 scenarios with
their required fail-closed expectations) · Validator: `tools/g0/validate_adversarial.py` → **PASS**

## Scenario-by-scenario results

| # | Scenario | Test | Result |
|---|---|---|---|
| A1 | stale deadline (cached portal vs official amendment) | `test_a1_...` | PASS — official wins, old value kept as SUPERSEDED lineage |
| A2 | equal-authority conflict | `test_a2_...` | PASS — CONFLICTED, critical use blocked |
| A3 | search snippet hallucination | `test_a3_...` | PASS — snippet cannot promote |
| A4 | model-generated fake citation | `test_a4_...` | PASS — rejected/provisional |
| A5 | web prompt injection | `test_a5_...` | PASS — inert, policy unaffected |
| A6 | parser corrupts table (250k → 25k) | `test_a6_...` | PASS — verified promotion blocked |
| A7 | API schema drift | `test_a7_...` | PASS — DEGRADED, no silent nulls |
| A8 | user-provided EIN conflict | `test_a8_...` | PASS — USER_ASSERTED never outranks verified; identity review |
| A9 | county/city statistic mismatch | `test_a9_...` | PASS — blocked/qualified |
| A10 | old Census vintage | `test_a10_...` | PASS — stale under latest-vintage policy |
| A11 | deleted webpage | `test_a11_...` | PASS — retained snapshot replayable subject to retention |
| A12 | crawler redirect to unrelated domain | `test_a12_...` | PASS — blocked/flagged |
| A13 | duplicate same-content retrieval | `test_a13_...` | PASS — no duplicate bytes; retrieval timing preserved |
| A14 | material amendment after D0 draft | `test_a14_...` | PASS — D0 packet/draft marked stale |
| A15 | nonmaterial formatting change | `test_a15_...` | PASS — no unnecessary invalidation |
| A16 | source adapter self-promotion | `test_a16_...` | PASS — policy rejects; promotion service governs |
| A17 | missing raw snapshot | `test_a17_...` | PASS — NON_REPLAYABLE |
| A18 | cross-tenant source upload | `test_a18_...` | PASS — tenant scoping enforced |
| A19 | malicious uploaded DOCX/PDF | `test_a19_...` | PASS — quarantine path |
| A20 | amount units mismatch | `test_a20_...` | PASS — normalization catches unit discrepancy |
| A21 | date timezone ambiguity | `test_a21_...` | PASS — unresolved, no silent midnight |
| A22 | private old page vs current issuer | `test_a22_...` | PASS — current issuer precedence |
| A23 | award-opportunity linkage without proof | `test_a23_...` | PASS — no fabricated linkage |
| A24 | causal inference from winner cohort | `test_a24_...` | PASS — descriptive allowed, causal blocked |
| A25 | retention deletion breaks evidence | `test_a25_...` | PASS — evidence demoted/replay status changed |

## C26 integration guarantees (also adversarial)

`tests/g0/book3/test_integration_property.py` — **28 passed** — proves the 22
mandatory invariants (every enabled source registered, material facts trace to
snapshots, snapshots immutable, promotion policy engine-independent, P0 changes
invalidate dependents, D0 packets reconstruct without agent memory, etc.) and
the 6 deterministic property tests (hashing idempotent, precedence/freshness/
invalidation deterministic, provenance graph without orphan facts, replay
preserving source identities).

## Verdict

**P0 adversarial coverage: PASS** (`adversarial_p0_pass: true`, `p0_open: 0` in
`G0_B3_REALITY_LOCK.json`). No scenario required a repair; every expectation in
the plan's C25 chapter is executed by a real test against live prototypes.
