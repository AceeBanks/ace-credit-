# G0 Book 5 — Contradiction & Resolution Model

**Chapter:** B5.C6 · **Config:** `config/g0/evidence/contradiction_types.yaml`
· **Schemas:** `contradiction.schema.json`, `resolution_event.schema.json`

## Contradiction object

```yaml
contradiction_id, subject_scope, predicate, claim_refs, contradiction_type,
severity, status, opened_at, resolved_at, resolution_event_ref
```

Types: VALUE_CONFLICT, IDENTITY_CONFLICT, TEMPORAL_CONFLICT,
SOURCE_REVISION_CONFLICT, SCOPE_CONFLICT, UNIT_CONFLICT,
INTERPRETATION_CONFLICT. **Unit mismatch is detected before value conflict.**

Resolution statuses: OPEN, RESOLVED_SOURCE_PRECEDENCE, RESOLVED_TEMPORAL,
RESOLVED_HUMAN, RESOLVED_CORROBORATION, SUPERSEDED, UNRESOLVED_ACCEPTED.

## Hard rules

- CONTR-001 — "higher model confidence" is never a valid resolution policy;
- CONTR-002 — equal-authority conflicts stay OPEN until governed resolution;
- CONTR-003 — newer source does not auto-win when historical dates differ;
- CONTR-004 — unit mismatch recognized before value conflict;
- CONTR-005 — human resolution is audited (approval ref required);
- CONTR-006 — the losing claim is retained (EVID-LAW-005, append-only).

## ResolutionEvent

Preserves all conflicting claims, the chosen operational fact, policy/reason,
actor/approval, time and downstream invalidation refs.

## Tests

`tests/g0/book5/test_contradictions.py` — 11 tests incl. confidence-block,
equal-authority-open, human-audit, losing-claim retention, corroboration
independence, unit detection.
