# G0-B7-C10 — Research Quality Evaluation

**Document ID:** GS-G0-B7-C10-RES
**Status:** RATIFIED (Book 7 chapter C10)
**Engine:** `prototype/g0/evaluation/domain_eval.py`
**Finding contracts:** Book 5 `research.py` (FIND-001..006)

## Evaluated for

- source coverage
- authority mix
- historical award identity correctness
- funder-priority grounding
- community statistic correctness (geography/unit/period preserved)
- geography/time fit
- duplicate-source detection
- unsupported inference
- limitation disclosure (weak-sample winner patterns MUST carry limitations)
- usefulness to proposal strategy
- provenance completeness

## Rules

- Evidence required on every finding (FIND-001).
- Historical patterns are descriptive; causal language on weak samples fails
  (FIND-003).
- Sample size represented on range/pattern findings (FIND-004).
- Applicability declared so findings are never silently injected as facts
  (FIND-005).
- Generated research summaries cannot be recursively cited as their own
  evidence; chains bottom out at sources (FIND-006).
- Future targets are never represented as historical achievements
  (CLAIM-004 + C10 hard check).
