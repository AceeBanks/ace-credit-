# G0-B3 — Source Classification & Source Registry (C2-C3)

## Scope

Establishes the source **classification ontology** (G0-B3-C2) and the seeded **Source Registry** (G0-B3-C3). These are the fail-closed source-of-truth structures that Book 3's data-constitution pipeline depends on for capture, precedence, and trust evaluation.

## C2 — Source Classes

Config of truth: `config/g0/source/source_classes.yaml`

Each source is assigned exactly one non-`unspecified` class on registration. Classes are ordered by increasing promiscuity / decreasing independent trustworthiness:

| class_id | class_name | trust_index | notes |
|---|---|---|---|
| `government_issuer` | Government issuer | 5 | Issuer of the underlying record |
| `government_aggregator` | Government portal/aggregator | 4 | Government-official platform aggregating issuer data |
| `funder_program_data` | Funder/program data | 3.5 | Program sponsor's published data |
| `npo_reporting` | Nonprofit self-reported | 3 | Organization-submitted (subject to validation) |
| `community_member_provided` | Community member provided | 2.5 | Direct from a person/entity involved |
| `third_party` | Third-party / intermediary | 2 | Vendors, brokers, intermediaries |
| `crowdsourced` | Crowdsourced | 1.5 | Openly contributed / unaudited |
| `composite` | Composite derived set | 1 | Derived from multiple lower classes |
| `document_scan` | Document/scan artifact | 2.5 | Scanned or OCR source (context-dependent) |
| `unspecified` | Unspecified / unmapped | 0 | Default; never acceptable for a registered source |

Registry rows carry a `domain_categories` set and a `trust_index_override` optional field; the override must be within `[0, 5]`.

## C3 — SourceRegistry Prototype

Config of truth: `config/g0/source/source_registry.yaml`

The seed registry contains 8 sources spanning issuers, aggregators, NPO reporting, community, third-party, and composite classes, each with either `api_base_url` or `base_urls` and a `data_type`/`update_cadence`/`data_license`.

Prototype: `prototype/g0/source/registry.py` (added C4-C5) — this chapter's validator verifies:

1. Exactly one non-`unspecified` class per source.
2. URL presence (`api_base_url` XOR `base_urls`).
3. Known class membership, known domain categories.
4. Optional `trust_index_override` within `[0, 5]`.
5. Unique source IDs, resolvable source classes.

## Validation

- Validator CLI: `python tools/g0/validate_source_registry.py` → **PASS**
- Test suite: `tests/g0/book3/test_source_registry.py` → 19 passed (class ordering, uniqueness, URL contract, default class rejection, override bounds)

## Commits

- `G0-B3-C2-C3` chapter band (this document accompanies the registry/class configs).

## Status

PASS — source classification and seeded registry are coherent, fail-closed, and under test.