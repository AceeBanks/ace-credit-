# D2 — Comparison Report (Baseline vs Humanized)

**Experiment:** D2 — FIRST GROUNDED GRANT-WRITING QUALITY EXPERIMENT
**Label:** MOCK_NON_SUBMISSION (submission enabled: False)

## Baseline Grounded Draft (deterministic, evidence-anchored)

- Requirement coverage: 1.0 (2/2 mandatory)
- Material claim support rate: 1.0 (supported 4/4)
- Unsupported material claims: 0
- Deterministic QA: 8/8 passed
- Budget total: 50000.00 (ceiling 50000.00)
- Eligibility: ELIGIBLE

## Humanized Grounded Draft

- **Status: AVAILABLE**
- governed model runtime configured; live lane executed through tools/g0/d2_live.py (see d2-live/ artifacts)

## Humanizer protected-claim diff (HZR-007)

- Identity transform preserves protected facts: True
- Tampered amount/deadline detected: True

## Metrics (Baseline)

| Dimension | Value |
|---|---|
| Requirement coverage | 1.0 |
| Claim support rate | 1.0 |
| Unsupported claims | 0 |
| Budget reconciled | True |

## Humanized metrics

BLOCKED_MODEL_RUNTIME — no model-generated humanized draft exists; no humanized metrics are fabricated.

## Limitations

- single fixture (GA-1); initial quality experiment, not proof across grants (C28 statistical discipline)
- humanized lane blocked: no model runtime
- no human edit-burden measurement (no reviewer)
- cost/latency reflect deterministic gates, not model inference

## Disposition

Humanizer: **DEFER (no live run)** — D2 does not automatically promote Humanizer; promotion requires a baseline-vs-candidate comparison through the Book 7 promotion path.