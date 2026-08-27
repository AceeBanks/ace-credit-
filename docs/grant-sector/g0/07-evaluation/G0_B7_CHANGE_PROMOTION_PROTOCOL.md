# G0-B7-C19/C21 — CandidateChange & Change Promotion Protocol

**Document ID:** GS-G0-B7-C19-21-PROMO
**Status:** RATIFIED (Book 7 chapters C19-C21)
**Schema:** `schemas/g0/evaluation/candidate_change.schema.json`,
`schemas/g0/evaluation/promotion_decision.schema.json`
**Config:** `config/g0/evaluation/promotion_thresholds.yaml`
**Engine:** `prototype/g0/evaluation/promotion.py`

## CandidateChange

Any proposed improvement becomes a typed candidate:

```yaml
candidate_change_id:
change_type: PROMPT | SKILL | MODEL | ROUTE | PARSER | RETRIEVAL |
            WORKFLOW | CONFIG | MEMORY_POLICY | CONTEXT_ASSEMBLY |
            TOOL_ADAPTER | RUNTIME_COMPONENT | RUBRIC_EVALUATOR
baseline_version:
candidate_version:
source_or_generator:
reason:
expected_benefit:
risk_class:
affected_capabilities:
required_eval_suites:
rollback_ref:
status:
```

Constitution/policy changes follow stricter governance and cannot masquerade
as ordinary candidate changes.

## PromotionDecision

Must include:

- baseline/candidate run refs
- eval corpus/suite versions
- metric comparison
- hard-gate results
- reviewer/approval where required
- reason codes
- rollout policy
- rollback ref

## Rules (PROM-001..007)

1. All hard-gate dimensions must pass.
2. Any HARD dimension regression vetoes.
3. Optimization dimensions may trade off only with documentation and no hard
   gate regression (Pareto).
4. Increased unsupported claims always veto (C8 hard gate).
5. Candidate generators cannot self-promote.
6. Rollback identity required before promotion.
7. At least one optimization dimension must improve by a minimum margin
   (5%) for PROMOTE; otherwise DEFER.

## No direct-write

No candidate framework may directly overwrite production Hermes skill
directories or production policy. Promotion changes production behavior only
through a PromotionDecision with rollback identity (EVAL-LAW-008/009).
