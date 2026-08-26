# G0-B3 — Source Classification & Source Registry (C2-C3)

## Scope

Establishes the source **classification ontology** (G0-B3-C2) and the seeded **Source Registry** (G0-B3-C3). These are the fail-closed source-of-truth structures that Book 3's data-constitution pipeline depends on for capture, precedence, and trust evaluation.

## C2 — Source Classes

Config of truth: `config/g0/source/source_classes.yaml`

Each source is assigned exactly one known class on registration. Authority is ALWAYS source + fact class: a source class alone never bypasses fact-specific precedence (C8).

| class_id | authority_tier | notes |
|---|---|---|
| `OFFICIAL_ISSUER` | A | Organization/agency issuing an opportunity, solicitation or guidance |
| `OFFICIAL_AGGREGATOR` | B | Government/official platform aggregating issuer data |
| `OFFICIAL_TRANSACTIONAL` | B | Official award/transaction record |
| `OFFICIAL_STATISTICAL` | B | Government/statistical authority |
| `TRUSTED_CURATED` | C | High-quality institutional secondary/aggregated source |
| `GOVERNED_WEB` | D | Registered funder/organization/research webpage captured by crawler |
| `USER_PROVIDED` | E | Client uploads/statements/manual data |
| `DERIVED_INTERNAL` | — | Product-derived structured data (external_authority: false) |

Recognized authority tiers are `[A, B, C, D, E]`. `DERIVED_INTERNAL` explicitly carries `external_authority: false` and no tier — derived internal objects cannot pretend to be external authority.

## C3 — SourceRegistry Prototype

Config of truth: `config/g0/source/source_registry.yaml`

The seed registry contains the full field contract from the plan and 8 sources: Grants.gov, Simpler.Grants.gov, USAspending, IRS EO Search, Census ACS, GA OPB/Grants Portal, GA DCA, and Foundation XYZ — covering OFFICIAL_AGGREGATOR, OFFICIAL_TRANSACTIONAL, OFFICIAL_STATISTICAL, OFFICIAL_ISSUER, and GOVERNED_WEB classes.

The validator verifies (fail-closed):

1. Every source has a known, classified `source_class` and matched `authority_tier`.
2. Full field contract compliance (`api_base_url` XOR `base_urls`, `terms_policy_ref`, `adapter_version`, `credential_scope_ref` where auth required, etc.).
3. Unique source IDs.
4. `external_authority` semantics for derived-internal sources.

## Validation

- Validator CLI: `python tools/g0/validate_source_registry.py` → **PASS**
- Test suite: `tests/g0/book3/test_source_registry.py` → 19 passed (class ordering, uniqueness, URL contract, default class rejection, override bounds)

## Commits

- `G0-B3-C2-C3` chapter band (this document accompanies the registry/class configs).

## Status

PASS — source classification and seeded registry are coherent, fail-closed, and under test.