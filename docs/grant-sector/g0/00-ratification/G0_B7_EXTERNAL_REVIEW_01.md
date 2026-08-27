# G0 Book 7 — External Review Record 01

**Review id:** `G0_B7_EXTERNAL_REVIEW_01`
**Reviewed surface:** Book 7 evaluation/promotion system
(`prototype/g0/evaluation/`, `config/g0/evaluation/`, `tools/g0/d2_harness.py`,
Book 7 Reality Lock, D2 experiment record, external-component decision ledger
Batch 07, Humanizer Amendment 003).
**Review range:** `49b84a659872c66e22aa954bdc480c25d51453c6`
**Date:** 2026-08-27

## Review status

| Stage | Status |
|---|---|
| External review finding | **REPAIR_REQUIRED** |
| Repair commit | `G0-B7-REPAIR-01: separate harness readiness from live evaluation evidence` |
| Post-repair verification | see below |
| External review resolution | `EXTERNAL_REVIEW_REPAIR_COMPLETE` — **AWAITING_EXTERNAL_RATIFICATION** |

## Overall assessment

**No P0 security/authority defect found in Book 7.** The Book 7 architecture
(evaluation constitution, quality taxonomy, eval-case/corpus/golden-set
contracts, deterministic-first gates, evaluator governance, single promotion
path, shadow/canary/rollback, adversarial + integration suites, D2 harness,
Reality Lock) remains intact. **No rollback or rewrite required.**

The findings below are evidence-semantics defects: the repository truthfully
reports that the live writing lane was never executed, but several
predicates/ledger entries asserted readiness as if it had been.

## Finding P1-01 — Humanizer disposition/status inconsistency

**Severity: P1 (evidence semantics).**

Three authoritative artifacts disagreed about the Humanizer state:

- Amendment 003: `BOUNDED STYLE_TRANSFORM CANDIDATE` (evaluation only).
- D2 experiment record + Book 7 checkpoint: `DEFER (no live run)`.
- External component decision ledger Batch 07: `ADOPT_BOUNDED`.

`ADOPT_BOUNDED` implies an adoption decision was made; no live
baseline-vs-humanized comparison exists, so no adoption decision is yet
justified.

**Correct present state:** `CANDIDATE / DEFER_PENDING_LIVE_BAKEOFF` —
bounded contract ratified, protected-claim guards implemented, live transform
not performed.

## Finding P1-02 — Reality Lock conflates harness readiness with live bake-off completion

**Severity: P1 (overstated readiness).**

The Book 7 Reality Lock asserted `humanizer_bakeoff_complete = true` while no
live Humanizer execution ever ran, and asserted the single broad
`ready_for_book8 = true` while the mission deliberately required a live D2
writing review before Book 8 execution.

**Repair:** the lock now distinguishes, truthfully and machine-readably:

- `humanizer_contract_pass` (contract ratified — true)
- `humanizer_bakeoff_harness_complete` (guards + harness — true)
- `humanizer_live_bakeoff_complete` (real transform+comparison — false)
- `humanizer_protected_claim_pass` (diff guards — true)
- `d2_harness_complete` (harness — true)
- `d2_live_model_run_complete` (real model draft — false)
- `d2_live_humanizer_run_complete` (real transform — false)
- `ready_for_book8_architecture` (Books 1–7 contracts/harnesses — true)
- `ready_for_book8_execution` (live D2 quality gate — false)

Book 7 remains `status = PASS` for its architecture while
`ready_for_book8_execution = false` because the live writing lane is blocked.

## Finding P2-01 — G0 evaluation thresholds are provisional, not production-calibrated

**Severity: P2 (calibration semantics).**

Several numeric thresholds are reasonable G0 defaults but are not yet
empirically calibrated:

- promotion `min_improvement: 0.05` (5%)
- routing cost justification `routed_cost < simple_cost * 0.9` (≥10% cheaper)
- parser locator hard gate `locator_lineage >= 0.9`

**Repair:** labeled machine-readably as
`calibration_status: PROVISIONAL_G0_DEFAULT`,
`recalibrate_from: BOOK8_MEASURED_EVIDENCE`. Thresholds are retained as
initial gates; no claim is made that they are empirically optimal.

## Outstanding items

- **Live D2 model test: still outstanding** (no authorized model runtime
  configured; recorded as `BLOCKED_MODEL_RUNTIME` without fabricated results).
- **Humanizer live bake-off: still outstanding** (same runtime block).
