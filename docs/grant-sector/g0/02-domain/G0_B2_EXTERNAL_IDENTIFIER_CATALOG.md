# G0 Book 2 — External Identifier Namespace Catalog (B2.C5)

**Source of truth:** `config/g0/domain/identifier_namespaces.yaml` (11 namespaces)
**Validator:** `tools/g0/validate_domain.py::validate_identifier_namespaces`
**Tests:** `tests/g0/book2/test_external_identifiers.py`

## Hard rule

> Never store an ambiguous field `external_id` without a namespace.

## Namespaces

| Namespace | Issuer | Applies to | Global unique |
|---|---|---|---|
| EIN | IRS | Organization | yes |
| UEI | SAM.gov | Organization | yes |
| ALN | SAM / Federal Register | Program | yes |
| GRANTS_GOV_OPPORTUNITY | Grants.gov | GrantOpportunity | yes |
| FAIN | awarding agency | Award | no |
| USA_SPENDING_AWARD | USAspending | Award | yes |
| SAM_ENTITY | SAM.gov | Organization | yes |
| FIPS | US Census | StatisticObservation, Organization | yes |
| GA_PORTAL | Georgia OPB / agency | GrantOpportunity, Program | no |
| COMMON_GRANTS | CommonGrants ecosystem | GrantOpportunity, ApplicationProject, Award | yes |
| PROVIDER | individual provider | Organization, GrantOpportunity, Award | no |

Each namespace carries `format`, `validation_rule`, `globally_unique`,
`temporally_unique`, `reusable`, `case_sensitive`, `normalization_rule` and
`verification_sources` (all validated).

## Semantics

- Provider IDs (GA_PORTAL, PROVIDER, FAIN) are **not globally unique** — they
  are scoped to their issuer; same string in two namespaces is two distinct
  identifiers (tested).
- Normalization is idempotent (EIN `58-1234567`, UEI uppercase, FIPS
  zero-padded).
- External IDs never replace internal primary identity (LAW-B1-022).
