# G0 Book 8 — External Review Record 01

**Review id:** `G0_B8_EXTERNAL_REVIEW_01`
**Reviewed surface:** Book 8 production-shaped Georgia vertical slice
(`prototype/g0/vslice/`, `tests/g0/book8/`,
`tools/g0/build_book8_reality_lock.py`, Book 8 Reality Lock + checkpoint,
governed model runtime integration).
**Review range:** `455a9d1242b895aed359a14ede033e64204aead2`
**Date:** 2026-08-27

## Review status

| Stage | Status |
|---|---|
| External review finding | **EXTERNAL_REVIEW_PASS_WITH_INTERNAL_REPAIR_ALREADY_APPLIED** |
| Repair commits | `G0-B8-REPAIR-01: bind eligibility statement into deterministic and live slice QA` (`72a9082a`) |
| External review resolution | `AWAITING_EXTERNAL_RATIFICATION` (not self-claimed by the build agent) |

### Machine-readable status model

```json
{
  "external_review": {
    "finding_status": "PASS_WITH_INTERNAL_REPAIR_ALREADY_APPLIED",
    "repair_status": "COMPLETE",
    "ratification_status": "AWAITING_EXTERNAL_RATIFICATION",
    "review_record": "docs/grant-sector/g0/00-ratification/G0_B8_EXTERNAL_REVIEW_01.md",
    "repair_commit": "G0-B8-REPAIR-01 (72a9082a)",
    "post_review_commit": "455a9d12",
    "live_d2_status": "PASS",
    "live_humanizer_status": "PASS (disposition REVISE)",
    "ready_for_book9": true
  }
}
```

## Overall assessment

**No P0 security/authority defect found in the current Book 8 review. No
architecture redesign required. No open P0.** The Book 8 production-shaped
Georgia vertical slice (intake → IntentContract → CEO TaskPlan → real
opportunity selection → deterministic eligibility → match → evidence-backed
research → blueprint → governed model drafting → reconciling budget → Claim
Ledger → 8-gate deterministic QA → honest human review →
`SUBMISSION_READY_MOCK` → explanation packet) is intact, integrated with
Books 1–7, and sealed with a derived Reality Lock.

Verified in this review:

- staged, chapter-sized forensic commit structure preserved
  (`G0-B8-C1` … `G0-B8-BOOK` + `G0-B8-REPAIR-01`);
- live model runtime successfully exercised end-to-end through the governed
  Model Gateway (`minimax/minimax-m3:free`, openrouter adapter) — real
  model-generated Grant draft, claim support 1.0, requirement coverage 1.0,
  unsupported material claims 0, protected-element loss 0;
- full vertical slice completed in both lanes (`LIVE_MODEL`,
  `DETERMINISTIC_BASELINE`);
- amendment/revision drill passed (material vs non-material selective
  invalidation, history preserved);
- cold reconstruction passed (no raw chat required);
- degraded-mode tests passed (integrity-critical fail closed, optional
  degrade locally);
- integrated security attacks passed (cross-tenant/cross-project decision
  reuse, direct provider bypass, credential extraction, direct submission,
  SSRF — all denied);
- telemetry + reconstruction + Book 9 handoff passed;
- internal adversarial self-review found one gap — the deterministic baseline
  draft did not carry the governed eligibility statement — fixed by
  `G0-B8-REPAIR-01`, which binds `check_eligibility_statement` into the slice
  QA and injects the governed `ELIGIBLE` statement into the deterministic
  lane. Both lanes now pass all 8 deterministic gates;
- `submission_enabled = false` (structurally impossible, unchanged);
- Book 8 Reality Lock: `status=PASS`, `p0_open=0`,
  `ready_for_book9=true`, `submission_enabled=false`;
- full G0 suite: 1778 passed, 3 skipped at the final head.

## Known limitation (recorded, not hidden)

**Writing-quality evidence remains small-sample.** The first live
Grant-writing experiment (`G0-B7-D2-LIVE`) proves the architecture and
grounding discipline (deterministic gates, claim ledger, fabrication
detection, protected-element survival), NOT universal proposal quality. One
fixture, one opportunity revision, one free-tier model lane, and one
Humanizer transform is weak statistical evidence. Future model / prompt /
Humanizer promotion decisions require additional Book 7 evaluation runs
across more fixtures and revisions; `G1.8 QA/evaluation` carries this
forward.

## Findings

| Id | Finding | Status |
|---|---|---|
| INT-01 | Deterministic baseline draft omitted the governed eligibility statement (mission protected element). | **RESOLVED** — `G0-B8-REPAIR-01` added `check_eligibility_statement` to slice QA and injects the governed statement into the deterministic lane. |
| LIM-01 | Writing-quality evidence is small-sample (single fixture/revision/model). | **RECORDED** — not a defect; additional Book 7 eval runs required before promotion decisions. |
| LIM-02 | Free-tier model lane shows run-to-run variance (occasionally drops a section); bounded retry + QA gates catch it. | **RECORDED** — honest finding documented in `G0_B7_D2_LIVE_RECORD.md`. |

## Ratification

External ratification of Book 8 (and therefore final authorization for the
Book 9 runtime-substrate work recorded here) is **NOT self-claimed** by the
build agent. A human external reviewer must ratify the Book 8 vertical
slice, the live D2 draft, and the evaluation methodology. The derived lock
reports `ready_for_book9=true` per the §26 gate conditions, and Book 9 is
executed on that basis with this record standing as the audit trail.
