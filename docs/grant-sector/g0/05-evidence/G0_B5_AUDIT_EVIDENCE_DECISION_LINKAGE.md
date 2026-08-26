# G0-B5-C18 — Audit ↔ Evidence ↔ Decision Linkage

## Purpose

Unify Book 1 audit events with Book 5 decision/evidence records so a
consequential action can be reconstructed forward and backward without
gaps.

## Forward path

```text
AuditEvent
→ PolicyDecision
→ Capability
→ DecisionRecord / Operation
→ Evidence inputs
→ Output artifacts
→ Human approval (if any)
```

## Backward path

```text
Proposal artifact
→ generating decision/task
→ evidence
→ actor
→ policy decision
→ audit event
```

## Rules (LINK-001..004)

1. Every consequential decision must be referenced by at least one audit
   event; an orphaned consequential decision is rejected.
2. An approval reference must resolve in the approval registry.
3. Actor and capability must be consistent between the audit event and the
   decision record.
4. Sensitive payload redaction preserves lineage fields (event ids, refs,
   actor, capability, policy/approval references, evidence inputs).

## Implementation

- `config/g0/evidence/linkage_policy.yaml` — policy
- `prototype/g0/evidence/linkage.py` — `forward_lineage`, `backward_lineage`,
  `check_orphaned_consequential`, `check_actor_capability_consistency`,
  `resolve_approval`, `redact_payload`
- `tools/g0/validate_linkage.py` — validator
- `tests/g0/book5/test_audit_linkage.py` — coverage incl. orphan rejection,
  approval resolution, actor/capability consistency, redaction preservation
