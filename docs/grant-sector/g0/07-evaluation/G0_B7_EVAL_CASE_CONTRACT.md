# G0-B7-C3 — EvalCase Contract

**Document ID:** GS-G0-B7-C3-CASE
**Status:** RATIFIED (Book 7 chapter C3)
**Schema:** `schemas/g0/evaluation/eval_case.schema.json`
**Prototype:** `prototype/g0/evaluation/models.py::EvalCase`

## Shape

```yaml
eval_case_id:
case_type:
corpus_version_id:
source_lineage_refs:
input_fixture_refs:
expected_assertions:
rubric_refs:
privacy_class:
tenant_scope:
label_origin:
reviewer_refs:
created_at:
valid_for_versions:
```

## Case types

- deterministic_rule
- structured_extraction
- grant_opportunity
- organization_profile
- eligibility
- matching
- research
- drafting
- budget
- qa
- personal_hermes_interaction
- ceo_orchestration
- worker_execution
- security_adversarial
- memory_reconstruction
- tool_execution

## Rules

1. **No case without lineage/fixture identity** (EVAL-LAW-007, EVAL-001):
   every case carries source snapshot refs or domain fixture refs plus
   decision/artifact refs.
2. **Label provenance** (EVAL-002): label_origin ∈ {HUMAN_REVIEWER,
   HUMAN_ATTESTED, MODEL_GENERATED, SYNTHETIC, DERIVED_FROM_EVIDENCE};
   label_reviewer required; model-generated labels are never presented as
   human gold.
3. **Immutability** (EVAL-003): content_hash pinned at creation; a changed
   source produces a NEW case, never a silent mutation of the recorded one.
4. **Synthetic labeling** (EVAL-004): synthetic cases are labeled synthetic.
5. **Privacy governance** (EVAL-005): TENANT_PRIVATE / RESTRICTED_SENSITIVE
   cases require governance approval before global eval.
6. Cases retain source/effective-date context for historical replay.
