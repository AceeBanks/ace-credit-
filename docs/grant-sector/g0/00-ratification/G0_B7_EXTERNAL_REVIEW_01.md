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

### Machine-readable status model

Per the Book 7 closeout mission, review status is not one overloaded field:

```json
{
  "external_review": {
    "finding_status": "REPAIR_REQUIRED",
    "repair_status": "COMPLETE",
    "ratification_status": "AWAITING_EXTERNAL_RATIFICATION",
    "review_record": "docs/grant-sector/g0/00-ratification/G0_B7_EXTERNAL_REVIEW_01.md",
    "repair_commit": "G0-B7-REPAIR-01 (72ad80d8)",
    "post_repair_commit": "G0-B7-EXT-REVIEW-01 post-repair record (4ca59800)",
    "live_d2_status": "BLOCKED_MODEL_RUNTIME",
    "live_humanizer_status": "BLOCKED_COMPONENT_RUNTIME"
  }
}
```

This structured form is mirrored in `G0_B7_BOOK_CHECKPOINT.json` and
`G0_B7_FINAL_TEST_MANIFEST.json`; all three reference the same final-head
evidence (`4ca59800`).

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

## Post-repair resolution (after `G0-B7-REPAIR-01` + `G0-B7-D2-LIVE-BLOCKED`)

| Finding | Status |
|---|---|
| P1-01 Humanizer disposition inconsistency | **RESOLVED** — ledger Batch 07 corrected to `CANDIDATE / DEFER_PENDING_LIVE_BAKEOFF`; Amendment 003 unchanged |
| P1-02 Reality Lock conflates harness readiness with live bake-off | **RESOLVED** — lock splits `humanizer_bakeoff_harness_complete` vs `humanizer_live_bakeoff_complete`, `d2_harness_complete` vs `d2_live_model_run_complete` / `d2_live_humanizer_run_complete`, `ready_for_book8_architecture` vs `ready_for_book8_execution` |
| P2-01 provisional thresholds | **RESOLVED / PROVISIONAL ACCEPTED** — labeled `PROVISIONAL_G0_DEFAULT`, recalibrate from `BOOK8_MEASURED_EVIDENCE`; retained as initial gates |

### Live lanes

| Lane | Result |
|---|---|
| D2 live model | **BLOCKED** (`BLOCKED_MODEL_RUNTIME`) — no authorized provider path in the governed G0 pipeline; no fabricated draft |
| Humanizer live | **BLOCKED** (`BLOCKED_COMPONENT_RUNTIME`) — no transform runtime; no fabricated draft |
| Humanizer disposition | **DEFER / CANDIDATE** (pending live baseline-vs-humanized comparison) |
| Submission | `submission_enabled = false` (unchanged) |

**External review status:** `EXTERNAL_REVIEW_REPAIR_COMPLETE` —
`AWAITING_EXTERNAL_RATIFICATION`. External ratification is NOT claimed by
this record; a human external reviewer must ratify before Book 8 execution
is authorized. Note also that `ready_for_book8_execution = false` regardless
(mission §20 condition 3 — live D2 model run — is not met).
