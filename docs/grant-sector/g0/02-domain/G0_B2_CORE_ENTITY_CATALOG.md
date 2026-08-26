# G0 Book 2 — Core Entity Catalog (B2.C3)

**Source of truth:** `config/g0/domain/entity_types.yaml` (21 root entities)
**Derived artifacts:** `schemas/g0/domain/*.json` via
`tools/g0/generate_domain_schemas.py` (never hand-written)
**Validator:** `tools/g0/validate_domain.py::validate_entity_types`
**Tests:** `tests/g0/book2/test_entity_boundaries.py` (catalog class)

## Entities

| Entity | Identity prefix | Revisioned by | State machine | Schema |
|---|---|---|---|---|
| Organization | `org_` | — | — | organization |
| Person | `person_` | — | — | person |
| OrganizationRole | `role_` | — | — | organization_role |
| ExternalIdentifier | `extid_` | — | — | external_identifier |
| Program | `program_` | — | — | program |
| GrantOpportunity | `opp_` | OpportunityRevision | opportunity | grant_opportunity |
| OpportunityRevision | `opp_rev_` | — | — | opportunity_revision |
| EligibilityRule | `rule_` | — | — | eligibility_rule |
| EligibilityDecision | `eldec_` | — | eligibility_decision | eligibility_decision |
| Award | `award_` | — | — | award |
| ApplicationProject | `app_` | ApplicationRevision | application_project | application_project |
| ApplicationRevision | `app_rev_` | — | — | application_revision |
| Requirement | `req_` | — | requirement | requirement |
| Budget | `budget_` | BudgetVersion | — | budget |
| CanonicalFact | `fact_` | — | canonical_fact | canonical_fact |
| EvidenceClaim | `claim_` | — | — | evidence_claim |
| StatisticObservation | `stat_` | — | — | statistic_observation |
| Artifact | `artifact_` | ArtifactVersion | artifact | artifact |
| OutcomeFeedback | `outcome_` | — | — | outcome_feedback |
| Relationship | `rel_` | — | — | relationship |
| CommonGrantsExtension | `cgx_` | — | — | common_grants_extension |

## Semantic contracts

- **Organization**: stable identity independent of any one grant source; kind,
  legal name, display name, status, jurisdiction. Sourced attributes live in
  the fact/evidence model, not on the root.
- **OpportunityRevision**: immutable terms; the exact target of eligibility,
  matching, requirements and application work (B2.C8).
- **EligibilityDecision**: deterministic result vs exact
  Organization state + OpportunityRevision + EligibilityRuleSet version;
  ELIGIBLE/INELIGIBLE/CONDITIONAL/UNKNOWN — never forced into true/false.
- **Award**: first-class root; exists without any internal ApplicationProject.
- **Money**: fixed-point decimal string in schemas — float money is
  prohibited (B2.C12) and enforced in every schema.

## Verification

- 21/21 schemas are generated from the catalog and checked current in tests.
- Every schema root type exists in the glossary (B2.C1 cross-check).
- Identity prefixes follow the B2.C4 semantic scheme and are unique.
