# G0 Book 2 — Relationship Catalog (B2.C6)

**Source of truth:** `config/g0/domain/relationship_types.yaml` (27 typed edges)
**Validator:** `tools/g0/validate_domain.py::validate_relationships`
**Prototype:** `prototype/g0/domain/relationships.py`
**Tests:** `tests/g0/book2/test_relationships.py`

## Contract

Every relationship type carries `relationship_type`, `source_entity_types`,
`target_entity_types`, `cardinality` (1:1 / 1:N / N:1 / N:M), `directed`,
`temporal`, `attributes`, `provenance_required` (and `no_self_loop` where
declared).

## Families

- **Organization:** ORGANIZATION_HAS_CONTACT, ORGANIZATION_HAS_PARTNER,
  ORGANIZATION_HAS_FISCAL_SPONSOR, ORGANIZATION_OPERATES_PROGRAM
- **Funding:** FUNDER_OFFERS_PROGRAM, PROGRAM_HAS_OPPORTUNITY,
  OPPORTUNITY_HAS_REVISION, AWARD_FUNDED_BY, AWARD_RECEIVED_BY,
  AWARD_UNDER_PROGRAM, AWARD_LINKED_TO_OPPORTUNITY
- **Application:** APPLICATION_FOR_ORGANIZATION,
  APPLICATION_TARGETS_OPPORTUNITY_REVISION, APPLICATION_HAS_REQUIREMENT,
  APPLICATION_HAS_ARTIFACT, APPLICATION_HAS_BUDGET, APPLICATION_USES_EVIDENCE,
  APPLICATION_HAS_OUTCOME
- **Evidence:** CLAIM_ASSERTED_BY_SOURCE_SNAPSHOT, FACT_SUPPORTED_BY_CLAIM,
  FACT_CONTRADICTED_BY_CLAIM, STATISTIC_DERIVED_FROM_SOURCE,
  ARTIFACT_USES_FACT, ARTIFACT_USES_STATISTIC,
  REQUIREMENT_SUPPORTED_BY_ARTIFACT

## Rules (tested)

- Endpoint types resolve against the B2.C3 catalog (+ `SourceSnapshot`, owned
  by Book 3); invalid endpoints rejected at runtime and in config.
- Cardinality enforced (e.g. STATISTIC_DERIVED_FROM_SOURCE is 1:1).
- Org-to-org edges (partner / fiscal sponsor) reject self-loops.
- Cross-tenant relationships rejected.
- Temporal edges support validity windows (versioned semantics).
- Graph rule: the catalog defines semantics regardless of whether the
  implementation later uses relational tables, graph projections or hybrid
  storage — Book 2 assumes no graph database.
