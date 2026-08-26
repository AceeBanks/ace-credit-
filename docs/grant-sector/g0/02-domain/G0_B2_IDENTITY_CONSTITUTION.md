# G0 Book 2 — Identity Constitution (B2.C4)

**Prototype:** `prototype/g0/domain/identity.py`
**Tests:** `tests/g0/book2/test_identity_semantics.py`

## Internal IDs

Every root entity receives an opaque stable internal ID with a semantic
prefix (B2.C3 scheme): `org_`, `person_`, `program_`, `opp_`, `opp_rev_`,
`award_`, `app_`, `app_rev_`, `artifact_`, `claim_`, `fact_`, `stat_`, ….
Semantics matter more than encoding; the prefix scheme is validated
(`validate_internal_id`).

## External IDs are attached identities

Every external identifier carries `namespace`, `value`, `entity_type`,
`issuer`, `valid_from/to`, `verification_state`, `source_lineage`.
**Hard rule:** never store an ambiguous `external_id` without a namespace.

## Entity resolution rule

| Status | Meaning |
|---|---|
| MATCH_CONFIRMED | shared VERIFIED issuer-authoritative ID (EIN/UEI) |
| MATCH_PROBABLE_REVIEW | name similarity without verified shared ID — propose, never silently merge |
| DISTINCT_CONFIRMED | conflicting VERIFIED IDs in an authoritative namespace |
| UNRESOLVED | insufficient evidence |

## Organization examples (all tested)

- Rename with same verified EIN → same Organization (new/superseded name fact).
- Similar names with different EINs → distinct Organizations.
- IRS + SAM + USAspending records → one internal Organization.
- Unverified/claimed IDs never confirm identity.

## Opportunity identity

- Same opportunity number, no issuer reissue → **same GrantOpportunity**; any
  amendment creates an `OpportunityRevision`.
- Issuer reissue or new number → **new GrantOpportunity** (explicit rule).

## Award identity

- Awards are never merged solely because recipient/funder/amount coincide;
  issuer award identifiers (FAIN/USAspending id) + program/time/context govern.
