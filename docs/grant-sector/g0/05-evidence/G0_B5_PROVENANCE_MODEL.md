# G0 Book 5 — Provenance Reference Model

**Chapter:** B5.C2 · **Schema:** `schemas/g0/evidence/provenance_ref.schema.json`

## One vocabulary

`ProvenanceRef` is the common reference for tracing data and outputs:

```yaml
ref_id, ref_type, entity_type, entity_id, version_or_revision_id,
tenant_id, content_hash, observed_at, effective_at, locator
```

`ref_type` covers SOURCE_SNAPSHOT, EXTRACTION_EVENT, NORMALIZATION_EVENT,
EVIDENCE_CLAIM, CANONICAL_FACT, STATISTIC_OBSERVATION, ELIGIBILITY_RULE,
ELIGIBILITY_DECISION, MATCH_DECISION, REQUIREMENT, RESEARCH_FINDING,
BUDGET_VERSION, ARTIFACT_VERSION, QA_RESULT, POLICY_DECISION, HUMAN_APPROVAL,
OUTCOME_FEEDBACK.

## Locator

A ref may carry a locator (URL+snapshot hash, PDF page, HTML selector, JSON
pointer, CSV row, cell range, text span, section id). Locators aid review but
never replace immutable snapshot identity (EVID-LAW-003).

## Guarantees (tested)

- every supported ref resolves to a typed object or an explicit tombstone;
- content-hash mismatch is detected (immutable identity);
- tenant mismatch is rejected;
- locator may be absent when object-level evidence is sufficient.

## Tests

`tests/g0/book5/test_provenance_graph.py` — provenance half.
