# G0-B7-C1 — Evaluation & Promotion Constitution

**Document ID:** GS-G0-B7-C1-EVALCON
**Status:** RATIFIED (Book 7 chapter C1)
**Branch:** `grant-sector-r0-salvage`
**Config of truth:** `config/g0/evaluation/evaluation_constitution.yaml`
**Validator:** `tools/g0/validate_evaluation_constitution.py`

This chapter freezes the laws governing quality claims and promotion. It
inherits and may not weaken Books 1–6 (Book 1 authority, Book 2 domain
semantics, Book 3/5 evidence authority, Book 4 Dual-Hermes separation,
Book 6 security gates).

## The governing loop

```text
OBSERVE → CANDIDATE → BASELINE → EVAL CORPUS → TEST → COMPARE →
HARD-GATE CHECK → PROMOTE | REVISE | REJECT | QUARANTINE →
SHADOW / CANARY → MONITOR → KEEP | ROLLBACK
```

No candidate generator owns promotion authority.

## EVAL-LAW-001 — Baseline required

No candidate is "better" without an explicit baseline and baseline version.

## EVAL-LAW-002 — Corpus/version required

Quality claims identify the exact evaluation corpus and suite version.

## EVAL-LAW-003 — Critical regressions veto aggregate improvement

A candidate cannot offset a security/authority/factuality P0 regression with
better style or lower cost.

## EVAL-LAW-004 — Deterministic assertions dominate subjective graders

Where correctness can be checked deterministically, use deterministic
evaluation.

## EVAL-LAW-005 — LLM judges are advisory unless independently anchored

Model graders may assess dimensions such as clarity/alignment, but cannot
alone authorize production promotion.

## EVAL-LAW-006 — Evaluator independence

A candidate should not be sole evaluator of itself. Use deterministic checks,
independent models, human review or combinations appropriate to risk.

## EVAL-LAW-007 — Evidence lineage required

Eval cases inherit Book 5 lineage.

## EVAL-LAW-008 — Promotion is explicit

No auto-writing candidate becomes production behavior without a
PromotionDecision.

## EVAL-LAW-009 — Promotion is reversible

Every promoted behavioral change has rollback identity and path.

## EVAL-LAW-010 — Security is non-compensatory

Book 1/6 violations are hard vetoes.

## EVAL-LAW-011 — Tenant privacy is non-compensatory

Cross-tenant leakage is P0 regardless of other scores.

## EVAL-LAW-012 — Production feedback is not automatically ground truth

User acceptance, win/loss, or downstream outcome may be informative but
requires interpretation and lineage.

## EVAL-LAW-013 — Quality dimensions remain visible

Do not collapse everything into one opaque score.

## EVAL-LAW-014 — Evaluation infrastructure is replaceable

Promptfoo, Hermes Eval Lab, Dojo, SkillClaw or any other tool sits behind
project-owned contracts.

## EVAL-LAW-015 — No silent online self-modification

G0 prohibits a production agent from observing itself and silently
rewriting/promoting its own skills/prompts/routes.

## Non-dilution list (inherited)

1. Personal Hermes and CEO Hermes are distinct optimization targets.
2. Workers remain bounded and non-sovereign.
3. Agent memory is not canonical truth.
4. Book 1 authority dominates every evaluation and rollout action.
5. Book 2 domain semantics remain sovereign.
6. Book 3/5 evidence authority cannot be replaced by evaluator opinion.
7. Book 6 security gates cannot be traded away for quality or speed.
8. External grant submission remains disabled in G0.
9. A model may participate in evaluation but may not be the sole judge of
   its own promotion; it cannot grade or promote itself by assertion.
10. Generated output is not evidence merely because another model scores it
    highly.
11. Tenant-private data cannot silently become global training/evaluation
    material.
12. No external skill/evolution framework may write directly into production
    behavior.
13. Improvement must be reversible.
14. Promotion decisions are first-class auditable DecisionRecords.
15. Quality claims require versioned evidence.
