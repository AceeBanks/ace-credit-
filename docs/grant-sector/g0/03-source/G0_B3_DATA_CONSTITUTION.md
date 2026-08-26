# G0 Book 3 — Chapter C1: Data Constitution

## Decision

Write the binding laws governing external data and evidence. 20 numbered laws,
each with an enforcement category (MUST/SHOULD), affected schemas/services and
amendment linkage to Books 1/2.

Machine-readable source of truth: `config/g0/source/data_constitution.yaml`.
Validator: `tools/g0/validate_data_constitution.py` (fail-closed).

## The 20 laws (all FROZEN)

| id | title |
|---|---|
| DATA-LAW-001 | Registered-source promotion |
| DATA-LAW-002 | Capture-before-interpretation |
| DATA-LAW-003 | Immutable source history |
| DATA-LAW-004 | Raw hash identity |
| DATA-LAW-005 | Transformation lineage |
| DATA-LAW-006 | Authority is source + fact class |
| DATA-LAW-007 | Freshness is domain-specific |
| DATA-LAW-008 | Stale critical facts may block action |
| DATA-LAW-009 | Conflicts remain explicit |
| DATA-LAW-010 | New revision never rewrites prior decision history |
| DATA-LAW-011 | Material source changes trigger invalidation |
| DATA-LAW-012 | Search result is not source evidence |
| DATA-LAW-013 | Generated citation is not evidence until verified |
| DATA-LAW-014 | Web content has no tool/policy authority |
| DATA-LAW-015 | Geography/time semantics mandatory for public statistics |
| DATA-LAW-016 | External IDs require namespace and verification state |
| DATA-LAW-017 | Source absence preserves uncertainty |
| DATA-LAW-018 | Data deletion does not falsify audit history |
| DATA-LAW-019 | Provenance is transitive |
| DATA-LAW-020 | Source adapters cannot promote themselves |

Amendment linkage is explicit where the law operationalizes a Book 1/2
constraint (e.g. DATA-LAW-001 → LAW-B1-007; DATA-LAW-010 → B2.C8;
DATA-LAW-016 → LAW-B1-022 + B2.C5).

## Tests (8 in `test_data_constitution.py`)

- all 20 laws present and frozen; validator passes
- laws carry linkage and affected schemas
- injected defects fail closed: missing law, duplicate id, unknown
  enforcement category, unfrozen law

Run: `python -m pytest tests/g0/book3/test_data_constitution.py -q` — **8 passed**.
Validator: `python tools/g0/validate_data_constitution.py` → exit 1 FAIL / 0 PASS.