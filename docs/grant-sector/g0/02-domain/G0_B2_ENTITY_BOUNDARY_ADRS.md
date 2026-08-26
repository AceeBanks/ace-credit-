# G0 Book 2 — Entity Boundary ADRs (B2.C2)

**Status:** RATIFIED (register: `G0_B2_ADR_REGISTER.md`)
**Proven by:** `tests/g0/book2/test_entity_boundaries.py`

Each ADR records decision, alternatives, rationale, consequences, affected
schemas, affected Book 1 capabilities, migration risk and status.

## ADR-B2-001 — Organization vs Funder vs Recipient

- **Decision:** `Organization` is the root legal/operational entity; `Funder`,
  `Recipient`, `Applicant`, `Partner` are `OrganizationRole` bindings.
- **Alternatives:** separate root entities per role; role as flat enum on Organization.
- **Rationale:** the same org may fund one program, receive another award, partner
  on a third and apply for a fourth; separate roots fragment identity.
- **Consequences:** role lookups traverse OrganizationRole; award/project refs point
  at organization_id + role context.
- **Affected schemas:** organization, organization_role, relationship.
- **Affected Book 1 capabilities:** organization.* (profile is one Organization).
- **Migration risk:** low (greenfield ontology).
- **Status:** RATIFIED.

## ADR-B2-002 — Program vs Opportunity

- **Decision:** `Program` is the ongoing funding/assistance structure; `GrantOpportunity`
  is a specific call under it. One Program → many Opportunities over time.
- **Alternatives:** merge into one entity; Opportunity without Program.
- **Rationale:** client tracks both the program relationship and each call;
  federal ALN maps to Program, not per-opportunity.
- **Consequences:** FUNDER_OFFERS_PROGRAM and PROGRAM_HAS_OPPORTUNITY relationships.
- **Affected schemas:** program, grant_opportunity.
- **Status:** RATIFIED.

## ADR-B2-003 — Opportunity vs OpportunityRevision

- **Decision:** stable `GrantOpportunity` identity; material source amendments create
  immutable `OpportunityRevision` objects. Eligibility/matching/application decisions
  point to the exact revision.
- **Alternatives:** mutate opportunity in place; treat each amendment as a new opportunity.
- **Rationale:** replay requires immutability (B2.C8); identity must survive amendment.
- **Consequences:** material-change detection gates revision creation; dependency
  staleness invalidation (B2.C8).
- **Affected schemas:** grant_opportunity, opportunity_revision, eligibility_decision,
  application_project.
- **Status:** RATIFIED.

## ADR-B2-004 — ApplicationProject vs interoperable Application

- **Decision:** internal `ApplicationProject` is the durable operational aggregate
  (workflow, evidence, requirements, artifacts, reviews, outcome lineage). A
  CommonGrants/public Application is an interoperability representation only.
- **Alternatives:** store everything in the external Application shape.
- **Rationale:** external representation must never truncate internal workflow
  semantics (B2.C15 loss-awareness).
- **Consequences:** CommonGrants mapping is EXACT/EXTENSION/LOSSY-classified.
- **Affected schemas:** application_project, application_revision, common_grants_extension.
- **Status:** RATIFIED.

## ADR-B2-005 — CanonicalFact vs EvidenceClaim

- **Decision:** `EvidenceClaim` = asserted/extracted proposition with provenance;
  `CanonicalFact` = promoted operational assertion under governance with lineage.
- **Alternatives:** single fact table; claim-is-fact.
- **Rationale:** B2.C9 — claims may conflict and coexist; promotion is governed.
- **Consequences:** FACT_SUPPORTED_BY_CLAIM / FACT_CONTRADICTED_BY_CLAIM edges.
- **Affected schemas:** evidence_claim, canonical_fact.
- **Status:** RATIFIED.

## ADR-B2-006 — Artifact vs SourceSnapshot

- **Decision:** `SourceSnapshot` captures external source state; `Artifact` is a
  system/client work product. Same physical PDF may play either role; semantic
  type determines the object.
- **Alternatives:** single "document" type.
- **Rationale:** evidence lineage vs deliverable lineage are different concerns.
- **Affected schemas:** artifact, source_snapshot (Book 3 owns snapshots in full).
- **Status:** RATIFIED.

## ADR-B2-007 — Requirement vs Response

- **Decision:** `Requirement` describes what the opportunity demands; `RequirementResponse`
  represents how the application satisfies it (section, form value, budget, attachment,
  certification placeholder, support letter).
- **Alternatives:** merge into one object.
- **Rationale:** a single requirement may be satisfied by multiple artifacts and
  vice versa; satisfaction state is tracked separately.
- **Affected schemas:** requirement, requirement_response.
- **Status:** RATIFIED.

## ADR-B2-008 — Proposal vs Business Plan

- **Decision:** both are Artifact families with distinct internal structures and
  purposes, sharing canonical facts where appropriate (LAW-B1-025).
- **Alternatives:** one generic document type with different filenames.
- **Rationale:** the plan forbids collapsing them; funder-response vs business-viability
  semantics differ.
- **Affected schemas:** artifact (artifact_type enum), application_project.
- **Status:** RATIFIED.

## ADR-B2-009 — Award as first-class root

- **Decision:** `Award` is a first-class root object linked to program/opportunity/
  funder/recipient — not merely an ApplicationProject status — because historical
  awards exist without our project.
- **Alternatives:** award as project status; award as relationship edge only.
- **Rationale:** winner intelligence (C17 AWARD-1) needs awards with no internal project.
- **Affected schemas:** award.
- **Status:** RATIFIED.

## ADR-B2-010 — Person vs OrganizationContact

- **Decision:** `Person` identity is distinct from the contextual `OrganizationContact`
  role/relationship linking a person to an organization.
- **Alternatives:** embed contact in Person; embed person in Organization.
- **Rationale:** one person may hold multiple contacts; PII stays minimal in core.
- **Affected schemas:** person, organization_role.
- **Status:** RATIFIED.
