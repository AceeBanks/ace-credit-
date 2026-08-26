# G0 Book 2 — Chapter C9: Fact, Claim, Evidence & Statistic Semantic Model

## Decision

Give Book 3 a clean semantic substrate for provenance. Claims are propositions;
CanonicalFacts are promoted operational assertions; quantitative public /
community data keeps its context instead of being flattened into a bare fact.

Machine-readable source of truth: `config/g0/domain/fact_semantics.yaml`.
Executable form: `prototype/g0/domain/facts.py` (+ invariants on `CanonicalFact`
in `prototype/g0/domain/models.py`).

## EvidenceClaim

A proposition with semantic scope and an expected value type — e.g.
"Organization has 501(c)(3) status", "Opportunity deadline is 2026-10-15",
"County poverty rate is X", "Program served 240 participants". Claims carry
`subject`, `predicate`, `value`, `value_type`, optional `source_snapshot_id`,
and a claim status (PROPOSED / VERIFIED / CONFLICTED / RETRACTED). Book 3
supplies full source/freshness mechanics.

## CanonicalFact

A promoted operational assertion with `subject`, `predicate`, `value`,
`value_type`, `scope`, valid/effective interval, `promotion_state`
(PROPOSED → PROMOTED → CONFLICTED / SUPERSEDED / RETIRED), supporting claim
refs and contradicting claim refs.

**Invariants (enforced at construction — fail closed):**

- A claim can NEVER automatically become a canonical fact: promotion is an
  explicit governed action (`promote_fact`), and
- a PROMOTED fact MUST reference ≥1 supporting claim;
- a CONFLICTED fact MUST reference ≥1 contradicting claim.

## Conflict semantics

Two claims may disagree without either being deleted. A canonical fact may
become CONFLICTED pending Book 3 resolution policy; the disagreeing claims are
preserved as evidence.

## StatisticObservation

Quantitative data is modeled WITH context: `metric`, `value` (Decimal only),
`unit`, `geography`, `reference_period`, `population` (required when the metric
is population-bearing), `dataset_version`, `methodology`/MOE. Geography, unit
and reference period are always required.

## Evidence use

Artifacts reference facts/statistics/claims through lineage objects rather than
copying unsupported prose into canonical state. `assertion_lineage()` resolves
`artifact_version_ref → fact → supporting claims → source snapshots` and fails
closed when any link is unresolvable.

## Tests (10 in `test_fact_evidence.py`)

- claim cannot automatically become canonical fact
- fact must reference support (constructor + promotion path)
- conflicting claims coexist without deletion; conflict requires contradictions
- statistic geography required; population required where relevant
- artifact traces assertion back to evidence object; unresolvable lineage fails
  closed
- fact-semantics validator: non-explicit promotion rule, promotion without
  support, missing statistic context field all fail closed

Run: `python -m pytest tests/g0/book2/test_fact_evidence.py -q`
Result: **10 passed**.
