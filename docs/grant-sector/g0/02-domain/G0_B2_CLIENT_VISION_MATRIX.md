# G0 Book 2 — Chapter C18: Client Vision Coverage Matrix

## Decision

Prove the ontology can represent the product the client asked for. Every Phase
1 client requirement maps to concrete domain entities, relationships, state
machine support and external mappings; **any uncovered requirement blocks Book
2 ratification**.

Machine-readable source of truth: `config/g0/domain/client_vision_matrix.yaml`.

## Coverage (31 requirements across five areas)

| Area | Count | Examples |
|---|---|---|
| Intake (CV-I) | 10 | organization identity, founder/contact, business concept, mission/vision, goals, target population, geography, program/project concept, financial assumptions, partnerships/evidence |
| Research & matching (CV-R) | 8 | opportunity, funder, program, historical awards/winners, eligibility rules/decision, match explanation, research evidence, community statistics |
| Document generation (CV-D) | 7 | proposal, business plan, pitch deck, financials, partnership/testimonial, goal sheets, research reports |
| Quality (CV-Q) | 6 | requirement coverage, factuality evidence, cross-document consistency, alignment, QA reports, review state |
| Submission-ready (CV-S) | 1 | package + readiness state WITHOUT representing actual submission |

## Eight grant categories

The client's eight categories (federal, state, local_county, foundation,
corporate, tribal, educational_institution, private_other) are supported
through **funding/opportunity metadata** on the single `GrantOpportunity`
entity (`opportunity_entity_rule:
single_grant_opportunity_entity_with_category_metadata`) — never eight
opportunity entity types.

## Validation

Every matrix row carries the plan's full format
(`client_requirement_id`, `domain_entities`, `relationships`,
`state_machine_support`, `external_mapping_if_any`, `covered`, `gap`).
`domain_entities` must resolve to real domain types (catalog entity types or
prototype model classes) — invented types are rejected.

## Tests (13 in `test_client_vision.py`)

- every Phase 1 requirement covered; all five areas represented
- per-area coverage completeness (intake 10, research 8, document 7, quality 6)
- submission-ready output without submission claim
- eight grant categories via a single opportunity entity
- domain entities are known types
- validator: uncovered requirement, wrong category set fail closed

Run: `python -m pytest tests/g0/book2/test_client_vision.py -q` — **13 passed**.
