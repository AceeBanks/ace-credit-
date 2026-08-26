# G0-B5-C19 — Evaluation Dataset Lineage

## Purpose

Prepare Book 7 so eval cases are trustworthy and reproducible. Every
benchmark/eval example derived from system work records full lineage.

## EvalCaseLineage

```text
case_id, source_snapshot_refs, domain_fixture_refs, decision/artifact_refs,
label_origin, label_reviewer, created_at, applicable_version,
privacy_classification, split_membership, content_hash, governance_approval
```

## Rules (EVAL-001..005)

1. Every case requires lineage (sources or fixtures, plus decision/artifact
   refs); cases without lineage are rejected.
2. Label provenance is required; model-generated labels are never presented
   as human labels.
3. Cases are immutable once recorded: a changed source must produce a new
   case, never silently mutate the historical one (content_hash pin).
4. Synthetic cases must be labeled synthetic.
5. TENANT_PRIVATE / RESTRICTED_SENSITIVE cases require explicit governance
   approval before entering generalized evaluation or training.

## Implementation

- `config/g0/evidence/eval_lineage_policy.yaml`
- `schemas/g0/evidence/eval_case_lineage.schema.json`
- `prototype/g0/evidence/eval_lineage.py` (`validate_eval_case`,
  `assert_unchanged`, `global_eval_export`)
- `tools/g0/validate_eval_lineage.py`
- `tests/g0/book5/test_eval_lineage.py`
