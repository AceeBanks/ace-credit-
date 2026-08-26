# G0-B5-C20 — D0/D1 Evidence Readiness

## Purpose

Strengthen the early drafting milestones with inspectable evidence.

## D0 Shadow Draft

A D0 shadow draft now produces:

```text
Mock Proposal ArtifactVersion
+ Application Claim Ledger
+ Research Findings
+ Evidence graph/provenance refs
+ QA factuality result
+ ExplanationPacket
```

with a derived `evidence_label`:

- `EVIDENCE_COMPLETE` — claim ledger coverage ≥ threshold (0.6);
- `EVIDENCE_INCOMPLETE` — otherwise. Stylistic completeness never implies
  evidence completeness (DRAFT-001); `submission_ready` is always `false`
  for mocks (DRAFT-002).

## D1 Hermes Draft

- CEO Hermes receives evidence through a bounded `ContextBundle` scoped to
  tenant/project and requirement relevance — never unrestricted graph access
  (DRAFT-003).
- A worker receives only evidence relevant to its assigned
  requirements/sections (DRAFT-004).
- WorkerResult returns: draft content/artifact ref, claims created, evidence
  used, assumptions, unresolved evidence gaps, sidechain ref (DRAFT-005).
- Personal Hermes explanation must reflect the CEO decision packet: same
  outcome, same evidence refs, same uncertainty disclosures (DRAFT-006).

## Implementation

- `config/g0/evidence/draft_readiness_policy.yaml`
- `prototype/g0/evidence/draft_readiness.py`
- `tools/g0/validate_draft_readiness.py`
- `tests/g0/book5/test_draft_readiness.py`
