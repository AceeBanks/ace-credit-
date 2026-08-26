# G0 Book 5 — Evidence Constitution

**Chapter:** B5.C1 · **Status:** RATIFIED (machine-readable: `config/g0/evidence/evidence_constitution.yaml`)

## Why

Book 5 answers *"why does the machine believe this, where did it come from,
what contradicted it, what was known when a decision was made, which outputs
depended on it, and can the decision be replayed?"* The constitution below
freezes the laws every evidence/decision contract must obey. They are the
non-negotiable input for every later chapter of Book 5.

## Laws

| # | Name | Enforcement |
|---|---|---|
| EVID-LAW-001 | Every material operational claim must be lineage-capable | FAIL_CLOSED |
| EVID-LAW-002 | Generated text is not evidence | FAIL_CLOSED |
| EVID-LAW-003 | Evidence retains source identity through normalization | FAIL_CLOSED |
| EVID-LAW-004 | Claim→CanonicalFact promotion is explicit | FAIL_CLOSED |
| EVID-LAW-005 | Contradictory evidence is retained (append-only) | APPEND_ONLY |
| EVID-LAW-006 | Decisions pin exact input revisions/versions | FAIL_CLOSED |
| EVID-LAW-007 | Replay uses historical state, never silent current substitution | FAIL_CLOSED |
| EVID-LAW-008 | Retrieval is non-authoritative | FAIL_CLOSED |
| EVID-LAW-009 | Derived claims retain derivation lineage (method + version) | FAIL_CLOSED |
| EVID-LAW-010 | Evidence is tenant-scoped across graph/vector/retrieval | FAIL_CLOSED |
| EVID-LAW-011 | Public vs private client evidence remain distinguishable | FAIL_CLOSED |
| EVID-LAW-012 | Explanation reflects the actual decision evidence | FAIL_CLOSED |
| EVID-LAW-013 | Material amendments trigger selective dependency review | FAIL_CLOSED |
| EVID-LAW-014 | Confidence cannot override hard contradiction | FAIL_CLOSED |
| EVID-LAW-015 | Physical storage is replaceable; no framework owns identity | FAIL_CLOSED |

## Enforcement notes

- **FAIL_CLOSED** — the operation is refused unless the condition holds.
- **APPEND_ONLY** — history is extended with resolution/supersession events;
  nothing is erased.
- Law 002 means a model repeating a claim does not make it evidence: promotion
  requires EVID-LAW-004's governed event with a real support set.
- Law 015 is the exit guarantee: Semantica, graph stores and vector indexes
  are replaceable projections; the governed system of record is sovereign.

## Tests

`tests/g0/book5/test_evidence_constitution.py` — 10 tests prove the laws are
machine-readable, unique, complete, and that the validator fails on any
missing/unknown/weak law.
