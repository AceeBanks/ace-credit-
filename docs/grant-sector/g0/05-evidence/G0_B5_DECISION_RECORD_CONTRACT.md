# G0 Book 5 — Decision Record Contract

**Chapter:** B5.C7 · **Schema:** `decision_record.schema.json` · **Config:** `config/g0/evidence/decision_types.yaml`

## Contract

```yaml
decision_id, decision_type, tenant_id, project_id, actor_ref, capability_id,
created_at, effective_at, input_refs, configuration_refs, model_or_engine_ref,
policy_ref, result, reason_codes, explanation_data, output_refs, status,
supersedes_decision_id
```

Twelve decision types (ELIGIBILITY … POLICY_AUTHORIZATION) with a replay
mode: DETERMINISTIC / DETERMINISTIC_WITH_PROJECTION / MODEL_ASSISTED /
AUDIT_REQUIRED.

## Hard rules

- DEC-001 — a decision missing the exact opportunity revision fails validation;
- DEC-002 — deterministic decisions record engine version;
- DEC-003 — model-assisted decisions pin structured context refs;
- DEC-004 — supersession never mutates the old decision;
- DEC-005 — chain-of-thought is never stored as required replay state.

## Tests

`tests/g0/book5/test_decision_records.py` — 5 tests.
