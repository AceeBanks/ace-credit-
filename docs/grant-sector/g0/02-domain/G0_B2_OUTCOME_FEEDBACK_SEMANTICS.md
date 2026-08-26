# G0 Book 2 — Chapter C14: Outcome & Learning Feedback Ontology

## Decision

Prepare the domain for later tracking/self-improvement WITHOUT building tracking
now. Phase 1 does not require submission automation, but the domain must not
require a redesign to learn later from outcomes.

Machine-readable source of truth: `config/g0/domain/outcome_policy.yaml`.
Executable form: `prototype/g0/domain/outcomes.py`.

## OutcomeFeedback

`outcome_id`, `project_id?`, `award_id?`, `outcome_type`, `observed_at`,
`verified_at?`, `source_evidence_refs`, `reason_codes?`, `freeform_feedback?`.
Outcome types (7): SUBMITTED, AWARDED, REJECTED, WITHDRAWN, REVISION_REQUESTED,
NOT_SUBMITTED, UNKNOWN.

## Learning rule

An outcome does NOT automatically rewrite prompts or policies. It becomes
**evidence** for Book 7/self-improvement evaluation (`learning_evidence()` →
`doctrine_effect: none`). Recording an outcome leaves doctrine byte-identical
(`doctrine_unchanged()` guard).

## Linkage

- A historical award can exist without any ApplicationProject.
- An outcome may be linked to a project/award AFTER the fact; linkage is a
  separate immutable operation (`link_outcome`).

## Tests (8 in `test_outcomes.py`)

- historical award can exist without ApplicationProject
- outcome can be linked later (original untouched)
- rejection feedback preserved without becoming automatic doctrine
- learning never rewrites doctrine
- outcome carries source evidence refs
- validator: missing outcome type, automatic-doctrine learning fail closed

Run: `python -m pytest tests/g0/book2/test_outcomes.py -q` — **8 passed**.
