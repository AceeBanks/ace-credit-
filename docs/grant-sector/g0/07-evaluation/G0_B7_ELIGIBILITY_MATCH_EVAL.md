# G0-B7-C9 — Eligibility & Match Evaluation

**Document ID:** GS-G0-B7-C9-ELIG
**Status:** RATIFIED (Book 7 chapter C9)
**Engine:** `prototype/g0/evaluation/domain_eval.py`
**Domain engine:** `prototype/g0/domain/eligibility.py` (deterministic)

## Eligibility

Treat deterministic eligibility as classification/rule execution, not prose
grading. Measure:

- rule extraction accuracy
- hard-rule evaluation accuracy
- unknown handling (UNKNOWN/CONDITIONAL surfaced, never collapsed)
- false eligible rate (HIGH severity — a hard requirement must not pass)
- false ineligible rate
- revision sensitivity (new OpportunityRevision -> re-evaluation)
- explanation correctness

**False eligible on a hard requirement is higher severity than a
conservative unknown.**

The only path to an EligibilityDecision is the deterministic engine
(`evaluate_rule_set`); LLM narrative output can never directly set ELIGIBLE.

## Matching

Separate:

- hard eligibility (never overridable)
- relevance/alignment ranking
- strategic attractiveness
- evidence sufficiency

Match dimensions are kept visible (no one opaque "94% match"); the ranked
recommendation is derived deterministically from aligned dimensions, and an
INELIGIBLE opportunity can never be promoted by a high match score.
