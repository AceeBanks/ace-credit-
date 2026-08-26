# G0 Book 2 — Chapter C10: Eligibility Ontology & Deterministic Boundary

## Decision

Interpretation is separated from evaluation so Book 3/source extraction and G1
implementation share one contract:

```
solicitation language ──LLM/research worker──▶ candidate structured rule
candidate rule ──validation (schema/meaning)──▶ validated rule
validated rule + canonical facts ──▶ deterministic result
```

Machine-readable source of truth: `config/g0/domain/eligibility_policy.yaml`.
Executable form: `prototype/g0/domain/eligibility.py`.

## Rule structure

`rule_id`, `rule_type`, `subject_type`, `operator`, `expected_value`,
`unit_or_namespace`, `required_fact_types`, `source_requirement_ref`,
`severity`, `explanation_template`, `closed_world`.

Operators (all 13 from the plan): EQUALS, IN, NOT_IN, EXISTS, NOT_EXISTS, GTE,
LTE, BETWEEN, WITHIN_GEOGRAPHY, BEFORE/AFTER, BOOLEAN_TRUE,
CUSTOM_DETERMINISTIC_PREDICATE.

## Unknown semantics

Missing evidence yields **UNKNOWN** (aggregate: **CONDITIONAL**), never
fabricated eligibility. A fact counts as false only when the rule explicitly
declares `closed_world: true`. Aggregate semantics: any REQUIRED failure →
INELIGIBLE; else any UNKNOWN → CONDITIONAL; else ELIGIBLE.

## Decision reproducibility

Every decision records: rule-set id + version, opportunity revision,
fact/evidence version refs, per-rule results, aggregate result, explanation.
Evaluation is a pure function — same rule set + same facts → same decision.
A new opportunity revision supersedes the old decision (the old object is
immutable and goes stale via the B2.C8 revision machinery). LLM narrative
output can never directly set ELIGIBLE: the only path to a decision is
`evaluate_rule_set`.

## Tests (13 in `test_eligibility.py`)

- same inputs reproduce same decision
- missing fact does not become false unless closed-world declared
- any required failure → INELIGIBLE
- new opportunity revision supersedes old decision (immutable old, stale via C8)
- LLM narrative cannot directly set ELIGIBLE
- full operator matrix (10 operators)
- validator: unknown operator, missing-evidence semantics, narrative-can-set
  result all fail closed

Run: `python -m pytest tests/g0/book2/test_eligibility.py -q` — **13 passed**.
