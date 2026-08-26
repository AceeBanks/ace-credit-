# G0 Book 4 — Result Synthesis Protocol

**Document ID:** GS-G0-B4-C9-SYNTHESIS-001
**Version:** 1.0
**Status:** FROZEN
**Book:** B4.C9
**Schema:** `schemas/g0/agents/outcome_artifact.schema.json`
**Prototype:** `prototype/g0/agents/result_reducer.py`

---

## 1. Purpose

Define how multiple bounded worker outputs become **one coherent operational
result** — synthesis against evidence and state, not concatenation of
summaries.

## 2. Synthesis inputs

- structured outputs;
- promoted/verified evidence;
- task quality state;
- unresolved conflicts;
- deterministic results;
- application state.

## 3. OutcomeArtifact

```yaml
outcome_id:
intent_id:
plan_id:
application_project_id:
opportunity_revision_id:   # exact immutable revision — pinned
outcome_type:
status:                    # SUCCEEDED | INCOMPLETE | BLOCKED | FAILED | CONFLICTED
executive_summary:
key_decisions:
recommended_actions:
research_pack_refs:
artifact_refs:
unresolved_questions:
risks:
qa_refs:
evidence_refs:
client_action_required:
created_at:
```

## 4. Rules (frozen)

1. **Uncertainty is preserved.** Unresolved questions and risks flow through.
2. **Contradictory worker outputs are surfaced, not averaged.** Two disagreeing
   deadline claims produce `CONFLICTED` with the conflicting predicate
   recorded — never a silent middle value or majority vote.
3. **Failed critical tasks prevent success.** A FAILED critical task forces
   the outcome to FAILED; partial results yield INCOMPLETE/BLOCKED.
4. **Outcomes link to canonical state/artifacts** instead of duplicating
   documents, and pin the exact `application_project_id` +
   `opportunity_revision_id`.
5. **`client_action_required` is explicit.**

## 5. Verified behaviors

- `test_conflicting_results_not_averaged`
- `test_failed_critical_task_blocks_success`
- `test_outcome_pins_exact_opportunity_revision`
- `test_partial_results_incomplete`
