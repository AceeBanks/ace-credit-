# G0 Book 2 — Grant Domain Ontology & CommonGrants Interoperability Master Implementation Plan

**Document ID:** GS-G0-B2-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR CONTINUOUS EXECUTION AFTER BOOK 1 RATIFICATION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Parent plan:** `G0_FULL_MASTER_BUILD_BLUEPRINT_v1.0.md`  
**Receives from:** Book 0 R0 Ratification + Book 1 Product Constitution & Authority  
**Hands off to:** Book 3 Grant Intelligence Data Constitution

---

# 0. Book Mission

Book 2 defines the **semantic operating system of the grant product**.

Book 1 answered:

> Who may act, at what authority, under what constitutional constraints?

Book 2 answers:

> What exactly are the things those actors act upon, how are they identified, how do they relate, what states may they occupy, what changes create a new version, and what does each term mean everywhere in the system?

This book must eliminate the class of failures where different agents/services use the same word to mean different things or different words to mean the same thing.

Examples Book 2 must make impossible:

- Hermes calls a funding program an opportunity while an adapter calls the same object a grant;
- an application draft silently points to a newer solicitation revision than the one eligibility was evaluated against;
- a nonprofit rename creates a second Organization despite the same legal identity;
- two organizations with similar names are incorrectly merged;
- a public CommonGrants Application becomes confused with the richer internal project/workflow object;
- a claim extracted from a webpage is treated as a verified organization fact;
- a generated proposal file is confused with the source document from which evidence was extracted;
- an award recipient is represented differently depending on whether it came from USAspending, a Georgia source or client intake;
- a grant requirement and a proposal section are modeled as the same thing;
- a business plan and grant proposal become one generic document type with different filenames.

Book 2 is therefore not merely a database-schema exercise. It is the **shared language contract** for humans, Hermes, workers, deterministic services, APIs, storage, evaluation and future UI.

---

# 1. Book Theme

## Identity → Meaning → Relationship → Lifecycle → Interoperability → Draftability

The book proceeds in this order deliberately.

```text
BOOK 1 CONSTITUTION
        ↓
DOMAIN LANGUAGE / GLOSSARY
        ↓
ENTITY BOUNDARIES
        ↓
IDENTITY RULES
        ↓
RELATIONSHIPS
        ↓
STATE MACHINES / VERSIONING
        ↓
COMMON GRANTS MAPPING
        ↓
SCHEMAS + INVARIANTS
        ↓
CLIENT-VISION COVERAGE
        ↓
D0 MOCK-DRAFT READINESS
        ↓
BOOK 3 HANDOFF
```

A schema should not be written before its entity meaning is settled. An adapter should not be designed before identity/version semantics are settled. A mock proposal should not be generated before the system knows exactly which Organization, OpportunityRevision, EvidenceClaims and Requirements it is using.

---

# 2. Hard Inputs from Previous Books

Book 2 receives Book 1 invariants as **constraints**, not suggestions.

At minimum:

1. canonical truth lives outside agent memory;
2. external facts require provenance;
3. conflicting facts remain visible until resolved;
4. provider IDs are not internal primary identity;
5. tenant scope is mandatory;
6. deterministic constraints remain deterministic after normalization;
7. safe research/drafting is L2;
8. submission remains disabled;
9. proposal and business plan are distinct artifacts;
10. grant-specific research must be representable to the client;
11. dynamic grant alignment is required;
12. community/impact evidence is first-class;
13. source revisions are immutable lineage events;
14. material source changes invalidate dependent state;
15. replay must not depend on hidden agent memory;
16. future outreach/tracking/submission must extend the same domain rather than create parallel truth.

If Book 2 discovers that one of these makes the domain impossible or materially wrong, it must stop and issue a constitutional amendment request rather than silently redefine the law.

---

# 3. Book 2 Design Philosophy

## 3.1 Internal model first, external mappings second

The product owns its internal domain semantics.

CommonGrants, Grants.gov/Simpler, SAM, USAspending, Georgia sources, IRS/FAC, Census and future private/foundation sources are **external representations**.

They map into the internal model. They do not independently define internal truth.

## 3.2 Stable identity, mutable attributes

An entity's display name, address, status, description or source representation may change without necessarily changing its identity.

## 3.3 Version what materially changes meaning

Not every edit deserves a new business object, but material solicitation/application/evidence changes must remain replayable.

## 3.4 Facts, claims and evidence are different things

A statement extracted from a source is not automatically a canonical fact.

## 3.5 Workflow state is not identity

An ApplicationProject remains the same project while moving from research to drafting to review. A new workflow state does not create a new project identity.

## 3.6 Public interoperability must be loss-aware

Round-trip mappings must explicitly identify what is exact, extended, internal-only, external-only or lossy.

## 3.7 The ontology must support the actual client product

If the ontology can model a federal award perfectly but cannot cleanly represent the client's business concept, founder story, dynamic proposal alignment, community evidence, business plan, budget and mock grant draft, it is incomplete.

## 3.8 Avoid premature ontology maximalism

Do not attempt to encode every possible grant program in America before proving the core domain. Use extensible typed structures and explicit extension points.

---

# 4. Required Book 2 Artifact Set

```text
docs/grant-sector/g0/02-domain/
├── G0_B2_DOMAIN_GLOSSARY.md
├── G0_B2_ENTITY_BOUNDARY_ADRS.md
├── G0_B2_CORE_ENTITY_CATALOG.md
├── G0_B2_IDENTITY_CONSTITUTION.md
├── G0_B2_EXTERNAL_IDENTIFIER_CATALOG.md
├── G0_B2_RELATIONSHIP_CATALOG.md
├── G0_B2_STATE_MACHINE_CATALOG.md
├── G0_B2_VERSIONING_REVISION_POLICY.md
├── G0_B2_FACT_CLAIM_EVIDENCE_MODEL.md
├── G0_B2_APPLICATION_DOCUMENT_MODEL.md
├── G0_B2_COMMON_GRANTS_MAPPING.md
├── G0_B2_EXTENSION_NAMESPACE_POLICY.md
├── G0_B2_CLIENT_VISION_COVERAGE.md
├── G0_B2_GEORGIA_FEDERAL_FIXTURE_PLAN.md
├── G0_B2_D0_DRAFT_READINESS.md
├── G0_B2_ADR_REGISTER.md
├── G0_B2_TEST_REPORT.md
├── G0_B2_ADVERSARIAL_TEST_REPORT.md
├── G0_B2_REALITY_LOCK_REPORT.md
└── G0_B2_HANDOFF_TO_BOOK_3.md

schemas/g0/domain/
├── organization.schema.json
├── person.schema.json
├── organization_role.schema.json
├── external_identifier.schema.json
├── program.schema.json
├── grant_opportunity.schema.json
├── opportunity_revision.schema.json
├── eligibility_rule.schema.json
├── eligibility_decision.schema.json
├── award.schema.json
├── application_project.schema.json
├── application_revision.schema.json
├── requirement.schema.json
├── budget.schema.json
├── canonical_fact.schema.json
├── evidence_claim.schema.json
├── statistic_observation.schema.json
├── artifact.schema.json
├── outcome_feedback.schema.json
├── relationship.schema.json
└── common_grants_extension.schema.json

config/g0/domain/
├── entity_types.yaml
├── relationship_types.yaml
├── identifier_namespaces.yaml
├── state_machines.yaml
├── requirement_types.yaml
├── artifact_types.yaml
└── common_grants_mapping.yaml

prototype/g0/domain/
├── models.py
├── identity.py
├── transitions.py
├── mapping_common_grants.py
├── validators.py
└── fixtures/

tests/g0/book2/
├── test_entity_boundaries.py
├── test_identity_semantics.py
├── test_external_identifiers.py
├── test_relationships.py
├── test_state_machines.py
├── test_revision_semantics.py
├── test_fact_claim_evidence.py
├── test_application_document_model.py
├── test_common_grants_mapping.py
├── test_domain_invariants.py
├── test_client_vision_coverage.py
├── test_georgia_federal_fixtures.py
└── test_adversarial_domain.py
```

Paths may adapt to repository conventions, but artifact responsibilities may not disappear.

---

# 5. Chapter B2.C1 — Domain Glossary & Ubiquitous Language

## Objective

Freeze the vocabulary used by humans, agents, code, tests and UI.

## Required glossary classes

### Business actors and organizations

- Organization
- Person
- OrganizationRole
- Funder
- Recipient
- Applicant
- Partner
- Contact

### Funding structure

- Program
- Assistance Listing
- GrantOpportunity
- OpportunityRevision
- Award
- FundingInstrument
- FundingCategory

### Eligibility

- EligibilityRule
- EligibilityRuleSet
- EligibilityDecision
- EligibilityEvidence
- EligibilityStatus

### Application production

- ApplicationProject
- ApplicationRevision
- Requirement
- RequirementResponse
- ProposalSection
- BusinessPlanSection
- Budget
- BudgetLine
- Artifact
- ArtifactVersion
- SubmissionPackage

### Evidence

- SourceSnapshot
- EvidenceClaim
- CanonicalFact
- StatisticObservation
- EvidenceLink
- ConflictState

### Outcomes

- OutcomeFeedback
- AwardOutcome
- RejectionOutcome
- RevisionRequest

## Naming rule

Every glossary entry must include:

```yaml
term:
definition:
what_it_is_not:
identity_scope:
mutable_attributes:
source_of_truth_book:
examples:
common_confusions:
```

## Required distinctions

The glossary must explicitly distinguish:

```text
Program ≠ Opportunity
Opportunity ≠ OpportunityRevision
Opportunity ≠ Award
ApplicationProject ≠ ApplicationRevision
ApplicationProject ≠ SubmissionPackage
Requirement ≠ ProposalSection
EvidenceClaim ≠ CanonicalFact
StatisticObservation ≠ generic Fact
Artifact ≠ SourceSnapshot
Organization ≠ Funder
Organization ≠ Recipient
Funder/Recipient = roles where appropriate
Proposal ≠ Business Plan
Draft ≠ Approved Final
Submission-ready ≠ Submitted
```

## Tests

- no duplicate canonical terms;
- no circular definitions;
- every schema root type exists in glossary;
- every capability resource type from Book 1 maps to a glossary/domain object;
- banned ambiguous aliases flagged.

## Commit

`G0-B2-C1: freeze grant-domain ubiquitous language`

---

# 6. Chapter B2.C2 — Entity Boundary ADRs

## Objective

Resolve the high-cost modeling decisions before schemas are treated as authoritative.

## ADR-B2-001 — Organization vs Funder vs Recipient

Recommended model:

- `Organization` is the root legal/operational entity;
- `Funder`, `Recipient`, `Applicant`, `Partner` are roles/relationships unless a source requires a specialized extension.

Why:

The same organization may fund one program, receive another award, partner on a third project and apply for a fourth. Separate root tables/entities would fragment identity.

## ADR-B2-002 — Program vs Opportunity

`Program` represents an ongoing funding/assistance structure.

`GrantOpportunity` represents a specific opportunity/call under which an applicant may pursue funding.

One Program may produce many Opportunities across time.

## ADR-B2-003 — Opportunity vs OpportunityRevision

The opportunity has stable internal identity.

Material source amendments create `OpportunityRevision` objects.

Eligibility/matching/application decisions point to the exact revision used.

## ADR-B2-004 — ApplicationProject vs interoperable Application

Internal `ApplicationProject` is the durable operational aggregate containing workflow, evidence, requirements, artifacts, reviews and outcome lineage.

A CommonGrants/public Application is an interoperability representation/view of the relevant application data.

Do not let the external representation truncate internal workflow semantics.

## ADR-B2-005 — CanonicalFact vs EvidenceClaim

`EvidenceClaim` = a proposition asserted/extracted from a source or user input with provenance and status.

`CanonicalFact` = a promoted system assertion accepted for operational use under governance.

Claims can conflict. Canonical facts retain lineage to supporting claims/evidence.

## ADR-B2-006 — Artifact vs SourceSnapshot

`SourceSnapshot` captures external source state.

`Artifact` is a system/client work product such as proposal, business plan, research report, budget export or pitch deck.

A PDF can physically exist in either role; semantic role determines object type.

## ADR-B2-007 — Requirement vs Response

`Requirement` describes what the opportunity/application demands.

`RequirementResponse`/artifact/section represents how the application satisfies it.

## ADR-B2-008 — Proposal vs Business Plan

Both are Artifact families with distinct internal structures and purposes, sharing canonical organization/project facts where appropriate.

## ADR-B2-009 — Award as separate root object

Award should be a first-class root object linked to opportunity/program/funder/recipient rather than merely an ApplicationProject status because historical awards may exist without our application project.

## ADR-B2-010 — Person vs OrganizationContact

Person identity should remain distinct from the contextual role/contact relationship linking that person to an Organization.

## Deliverables

Each ADR must include:

- decision;
- alternatives;
- rationale;
- consequences;
- affected schemas;
- affected Book 1 capabilities;
- migration risk;
- status.

## Tests

Fixture scenarios must prove each boundary can represent real multi-role and historical cases without duplicate truth.

## Commit

`G0-B2-C2: ratify core entity boundary decisions`

---

# 7. Chapter B2.C3 — Core Entity Catalog

## Objective

Define the minimum semantic contract for every core entity.

## 7.1 Organization

Represents a stable organization identity independent of any one grant source.

Minimum semantic fields:

```text
organization_id
organization_kind
legal_name
preferred_display_name
status
jurisdiction
formation_date? 
primary_location?
created_at
updated_at
```

Do not put every sourced attribute directly on the root object. Detailed sourced facts belong through the fact/evidence model where appropriate.

Possible kinds:

- nonprofit;
- business;
- government entity;
- educational institution;
- tribal entity;
- fiscal sponsor;
- foundation;
- other governed extension.

## 7.2 Person

Stable person identity for founders, officers, contacts, reviewers and future external contacts.

Avoid unnecessary PII in the core schema.

## 7.3 OrganizationRole

Contextual role binding an Organization to another object/time period.

Examples:

- funder;
- applicant;
- recipient;
- partner;
- fiscal sponsor.

## 7.4 Program / AssistanceListing

Represents ongoing funding/assistance structure.

May map to federal ALN where applicable but must also support state/private programs without ALNs.

## 7.5 GrantOpportunity

Stable opportunity identity independent of revision.

## 7.6 OpportunityRevision

Immutable material representation/version of opportunity terms.

Must be the target for:

- eligibility evaluation;
- match calculation;
- requirement extraction;
- application project source revision.

## 7.7 EligibilityRule

Typed normalized rule.

Initial categories:

- applicant type;
- geography;
- registration/status;
- programmatic purpose;
- population served;
- financial threshold;
- matching requirement;
- experience/credential;
- deadline/time constraint;
- funding-use restriction;
- other explicit rule.

## 7.8 EligibilityDecision

Deterministic result against:

```text
Organization state
+
Project/Program facts
+
OpportunityRevision
+
EligibilityRuleSet version
```

Statuses:

- ELIGIBLE;
- INELIGIBLE;
- CONDITIONAL;
- UNKNOWN/INSUFFICIENT_EVIDENCE.

Never force uncertainty into true/false.

## 7.9 Award

Historical/current award event with funder, recipient, amount, dates, program/opportunity links and external IDs where available.

## 7.10 ApplicationProject

Internal aggregate representing our effort to pursue one opportunity for one organization/project context.

Must point to exact `OpportunityRevision`.

Contains/references:

- organization/applicant;
- project/program concept;
- requirements;
- eligibility decision;
- research/evidence;
- artifacts;
- budget;
- QA/review state;
- submission readiness;
- outcome feedback.

## 7.11 ApplicationRevision

Immutable/versioned application-state snapshot or coherent authored revision.

Do not mutate away prior client-approved/reviewed versions.

## 7.12 Requirement

Typed requirement extracted/normalized from opportunity/application instructions.

Types may include:

- narrative;
- attachment;
- form;
- certification;
- budget;
- eligibility proof;
- partnership/support;
- financial;
- formatting;
- deadline/submission;
- other.

## 7.13 Budget

Structured financial plan with deterministic arithmetic and lineage to narrative/project assumptions.

## 7.14 CanonicalFact

Promoted operational assertion with scope, effective time, support lineage and conflict status.

## 7.15 EvidenceClaim

Source/user asserted proposition awaiting/holding evidence status.

## 7.16 StatisticObservation

Quantitative observation with metric, value, unit, geography, population, reference period, dataset/version and methodology metadata.

Book 3 defines source/freshness mechanics in full; Book 2 defines semantic shape.

## 7.17 Artifact

System/client work product.

Initial artifact families:

- research report;
- match explanation;
- application blueprint;
- grant proposal;
- business plan;
- pitch deck;
- budget/financial;
- partnership/support material;
- testimonial material;
- goal sheet;
- QA report;
- submission package;
- client explanation.

## 7.18 OutcomeFeedback

Represents downstream outcome useful for learning:

- submitted;
- awarded;
- rejected;
- withdrawn;
- revision requested;
- unknown;
- future granular reasons/feedback.

## Commit

`G0-B2-C3: define core grant-domain entity catalog`

---

# 8. Chapter B2.C4 — Identity Constitution

## Objective

Make entity identity stable across source changes and source disagreement.

## 8.1 Internal IDs

Every root entity receives an opaque stable internal ID.

Recommended semantic IDs:

```text
org_...
person_...
program_...
opp_...
opp_rev_...
award_...
app_...
app_rev_...
artifact_...
claim_...
fact_...
stat_...
```

Implementation may use UUID/ULID/etc.; semantics matter more than encoding.

## 8.2 External IDs are attached identities

Examples:

- EIN;
- UEI;
- ALN;
- Grants.gov opportunity number;
- FAIN;
- USAspending award ID;
- SAM identifiers;
- FIPS;
- Georgia program/opportunity IDs;
- CommonGrants IDs;
- foundation/provider IDs.

Each identifier needs:

```yaml
namespace:
value:
entity_type:
issuer:
valid_from:
valid_to:
verification_state:
source_lineage:
```

## 8.3 Entity resolution rule

Resolution should produce:

- MATCH_CONFIRMED;
- MATCH_PROBABLE_REVIEW;
- DISTINCT_CONFIRMED;
- UNRESOLVED.

Probabilistic/name similarity may propose a merge but must not silently merge protected entities.

## 8.4 Organization examples

### Rename

```text
Old: Community Youth Works, Inc.
New: Georgia Youth Works, Inc.
Same verified EIN
→ same Organization, new/superseded name fact
```

### Similar name, different EIN

```text
Atlanta Youth Initiative
Atlanta Youth Initiatives Inc.
different EINs
→ distinct Organizations unless stronger evidence proves otherwise
```

### Same organization across sources

IRS, SAM, USAspending and Georgia award records may all map to one internal Organization.

## 8.5 Opportunity identity

Same opportunity number with amended solicitation:

```text
same GrantOpportunity
new OpportunityRevision
```

A completely reissued opportunity may require a new Opportunity depending on issuer semantics. Decision rule must be explicit.

## 8.6 Award identity

Do not merge awards solely because recipient/funder/amount match.

Use issuer award identifiers + program/time/context.

## Tests

- rename continuity;
- duplicate-name separation;
- cross-source organization resolution;
- source ID reuse/collision;
- amended opportunity revision;
- reissued opportunity;
- historical award dedupe;
- missing external ID;
- conflicting external IDs.

## Commit

Bundle with C5.

---

# 9. Chapter B2.C5 — External Identifier Namespace Catalog

## Objective

Prevent identifier ambiguity and provider lock-in.

## Required namespace metadata

```yaml
namespace_id:
name:
issuer:
applies_to_entity_types:
format:
validation_rule:
globally_unique:
temporally_unique:
reusable:
case_sensitive:
normalization_rule:
verification_sources:
```

## Initial namespaces

Federal:

- EIN/TIN where legally/operationally appropriate;
- UEI;
- ALN;
- Grants.gov opportunity number;
- FAIN;
- USAspending award ID;
- SAM identifiers;
- FIPS geographic codes.

Georgia:

- Georgia portal/program identifiers discovered during source onboarding;
- agency-specific identifiers as namespaced extensions.

Interoperability:

- CommonGrants identifiers where applicable.

Private/foundation:

- provider-specific IDs under explicit namespaces.

## Hard rule

Never store ambiguous field `external_id` without namespace.

## Tests

- namespace collision;
- normalization;
- invalid format;
- same value in two namespaces;
- historical validity windows.

## Commit

`G0-B2-C4-C5: freeze identity and external identifier semantics`

---

# 10. Chapter B2.C6 — Relationship Catalog

## Objective

Define typed edges instead of ad hoc foreign-key meaning.

## Relationship contract

```yaml
relationship_type:
source_entity_types:
target_entity_types:
cardinality:
directed:
temporal:
attributes:
provenance_required:
```

## Initial relationships

### Organization relationships

- ORGANIZATION_HAS_CONTACT → Person
- ORGANIZATION_HAS_PARTNER → Organization
- ORGANIZATION_HAS_FISCAL_SPONSOR → Organization
- ORGANIZATION_OPERATES_PROGRAM → internal project/program concept

### Funding relationships

- FUNDER_OFFERS_PROGRAM
- PROGRAM_HAS_OPPORTUNITY
- OPPORTUNITY_HAS_REVISION
- AWARD_FUNDED_BY
- AWARD_RECEIVED_BY
- AWARD_UNDER_PROGRAM
- AWARD_LINKED_TO_OPPORTUNITY where known

### Application relationships

- APPLICATION_FOR_ORGANIZATION
- APPLICATION_TARGETS_OPPORTUNITY_REVISION
- APPLICATION_HAS_REQUIREMENT
- APPLICATION_HAS_ARTIFACT
- APPLICATION_HAS_BUDGET
- APPLICATION_USES_EVIDENCE
- APPLICATION_HAS_OUTCOME

### Evidence relationships

- CLAIM_ASSERTED_BY_SOURCE_SNAPSHOT
- FACT_SUPPORTED_BY_CLAIM
- FACT_CONTRADICTED_BY_CLAIM
- STATISTIC_DERIVED_FROM_SOURCE
- ARTIFACT_USES_FACT
- ARTIFACT_USES_STATISTIC
- REQUIREMENT_SUPPORTED_BY_ARTIFACT

## Graph rule

The relationship catalog defines semantics whether implementation uses relational tables, graph projections, Semantica or hybrid storage later.

Book 2 must not assume a graph database.

## Tests

- invalid endpoint types rejected;
- cardinality rules enforced;
- temporal relationship versioning supported;
- impossible cycles detected where prohibited;
- cross-tenant relationship rejected.

## Commit

`G0-B2-C6: define typed domain relationship catalog`

---

# 11. Chapter B2.C7 — State Machine Catalog

## Objective

Prevent arbitrary string-status mutation.

## 11.1 GrantOpportunity state

Suggested conceptual states:

```text
DISCOVERED
→ ACTIVE
→ AMENDED
→ CLOSED
→ CANCELLED
→ ARCHIVED
```

`AMENDED` may be event/revision metadata rather than long-lived root state; implementation ADR must decide.

## 11.2 EligibilityDecision state

```text
PENDING_INPUTS
→ EVALUATED
→ SUPERSEDED
```

Decision result separately:

```text
ELIGIBLE
INELIGIBLE
CONDITIONAL
UNKNOWN
```

## 11.3 ApplicationProject state

Recommended high-level lifecycle:

```text
IDEA
→ QUALIFYING
→ RESEARCH
→ DRAFTING
→ QA
→ HUMAN_REVIEW
→ SUBMISSION_READY
→ [future SUBMITTED]
→ [future AWARDED | REJECTED | WITHDRAWN]
```

Phase 1 transition stops at `SUBMISSION_READY`.

## 11.4 Requirement state

```text
IDENTIFIED
→ NORMALIZED
→ IN_PROGRESS
→ SATISFIED
→ VERIFIED
```

Alternate terminal:

```text
NOT_APPLICABLE
BLOCKED
WAIVED (only if issuer/source supports it)
```

## 11.5 Artifact state

```text
DRAFT
→ QA_PENDING
→ REVIEW_REQUIRED
→ APPROVED_INTERNAL
→ SUBMISSION_READY
→ SUPERSEDED
```

## 11.6 CanonicalFact state

```text
PROPOSED
→ VERIFIED/PROMOTED
→ CONFLICTED
→ SUPERSEDED
→ RETIRED
```

## 11.7 OutcomeFeedback state

Must distinguish outcome observation from verified outcome.

## Transition contract

Every state transition defines:

- allowed from/to;
- capability required;
- authority level;
- preconditions;
- evidence requirements;
- audit class;
- invalidation consequences.

## Tests

- illegal transitions rejected;
- submission state unavailable in Phase 1;
- stale eligibility blocks `SUBMISSION_READY`;
- unsatisfied mandatory requirement blocks readiness;
- superseded opportunity revision triggers application review/re-evaluation.

## Commit

`G0-B2-C7: freeze domain state machines and transition semantics`

---

# 12. Chapter B2.C8 — Versioning, Revision & Temporal Semantics

## Objective

Make historical reconstruction possible without versioning everything indiscriminately.

## Root vs revision rule

Use stable root + immutable revision where material terms evolve.

### Opportunity

```text
GrantOpportunity
 ├─ Revision 1
 ├─ Revision 2
 └─ Revision 3
```

### Application

```text
ApplicationProject
 ├─ Revision 1
 ├─ Revision 2
 └─ Revision N
```

### Artifact

Artifact identity may represent logical document with immutable ArtifactVersions.

## Temporal fields

Distinguish:

- observed_at;
- retrieved_at;
- effective_from;
- effective_to;
- created_at;
- superseded_at.

Book 3 defines source freshness policy; Book 2 defines semantic meaning.

## Materiality

Material changes include, at minimum:

- deadline;
- eligibility;
- funding amount/ceiling/floor;
- match requirement;
- geography;
- required attachment;
- required narrative/question;
- submission method;
- cancellation;
- scoring/evaluation criteria when relevant.

## Dependency invalidation

An ApplicationProject must record the exact OpportunityRevision against which:

- eligibility was evaluated;
- match score was computed;
- requirements were normalized;
- draft was generated.

If a new material revision arrives, dependent decisions become stale until re-evaluated.

## Tests

- reconstruct application against revision N;
- new revision does not mutate old decision;
- material amendment marks dependent state stale;
- non-material formatting change need not invalidate eligibility;
- artifact version lineage remains intact.

---

# 13. Chapter B2.C9 — Fact, Claim, Evidence & Statistic Semantic Model

## Objective

Give Book 3 a clean semantic substrate for provenance.

## EvidenceClaim

Represents a proposition such as:

```text
"Organization has 501(c)(3) status"
"Opportunity deadline is 2026-10-15"
"County poverty rate is X"
"Program served 240 participants"
```

A claim includes semantic scope and expected value type but Book 3 supplies full source/freshness mechanics.

## CanonicalFact

A promoted operational assertion.

Required semantic concepts:

```text
subject
predicate
value
value_type
scope
valid/effective interval
promotion state
supporting claim refs
contradiction refs
```

## StatisticObservation

Do not model quantitative public/community data as a bare fact when context matters.

Must preserve:

- metric;
- value;
- unit;
- geography;
- population;
- reference period;
- dataset/version;
- methodology/MOE when applicable.

## Evidence use

Artifacts should reference facts/statistics/claims through lineage rather than copying unsupported prose into canonical state.

## Conflict semantics

Two claims may disagree without either being deleted.

Canonical fact can become CONFLICTED pending Book 3 resolution policy.

## Tests

- claim cannot automatically become canonical fact;
- fact must reference support;
- conflicting claims coexist;
- statistic geography/population required where relevant;
- artifact can trace factual assertion back to evidence object.

## Commit

`G0-B2-C8-C9: define revision and fact-evidence semantics`

---

# 14. Chapter B2.C10 — Eligibility Ontology & Deterministic Boundary

## Objective

Define what an eligibility rule is so Book 3/source extraction and later G1 implementation can separate interpretation from evaluation.

## Rule structure

```yaml
rule_id:
rule_type:
subject_type:
operator:
expected_value:
unit_or_namespace:
required_fact_types:
source_requirement_ref:
severity:
explanation_template:
```

## Operators

Examples:

- EQUALS;
- IN;
- NOT_IN;
- EXISTS;
- NOT_EXISTS;
- GTE;
- LTE;
- BETWEEN;
- WITHIN_GEOGRAPHY;
- BEFORE/AFTER;
- BOOLEAN_TRUE;
- CUSTOM_DETERMINISTIC_PREDICATE.

## Extraction boundary

LLM/research worker may propose:

```text
solicitation language
→ candidate structured rule
```

Validation then confirms the rule schema/meaning.

Evaluation is deterministic:

```text
validated rule
+
canonical organization/project facts
→ deterministic result
```

## Unknown semantics

Missing evidence yields UNKNOWN/CONDITIONAL, not fabricated eligibility.

## Decision reproducibility

EligibilityDecision stores:

- rule-set version;
- opportunity revision;
- fact/evidence versions;
- result per rule;
- aggregate result;
- explanation.

## Tests

- same inputs reproduce same decision;
- missing fact does not become false unless rule explicitly defines closed-world behavior;
- new opportunity revision supersedes old decision;
- LLM narrative output cannot directly set ELIGIBLE.

---

# 15. Chapter B2.C11 — Requirement & Application Content Model

## Objective

Represent the real grant-writing workload, not merely application metadata.

## Requirement object

Minimum concepts:

```text
requirement_id
opportunity_revision_id
requirement_type
source_location/reference
mandatory
prompt/instruction
constraints
word/page/character limit
formatting rules
required evidence
required attachments
due/submission semantics
normalized state
```

## RequirementResponse

Represents the application's response/satisfaction mechanism.

May point to:

- proposal section;
- form value;
- budget;
- attachment;
- certification placeholder;
- support letter;
- other artifact.

## ProposalSection

Must support dynamic section sets rather than hard-coding exactly 18 sections into the core ontology.

The client's 18-section model becomes a **proposal template/profile**, while actual solicitation requirements may add/remove/reorder sections.

This preserves client vision without forcing every funder's structure into one template.

## BusinessPlanSection

Separate section type/schema because business plan serves business viability/operations rather than funder-response semantics.

## Content alignment links

Sections may link to:

- requirements;
- canonical facts;
- evidence claims;
- statistics;
- project goals;
- budget lines;
- research findings.

## Cross-document consistency

Shared canonical facts should drive proposal/business plan/pitch deck/financials while each artifact retains its own purpose and narrative structure.

## Tests

- one requirement may require multiple artifacts;
- one artifact may satisfy multiple requirements only when explicitly linked;
- proposal/business plan remain distinct;
- dynamic solicitation section can coexist with client 18-section profile;
- unsupported partnership/testimonial cannot be invented as completed evidence.

---

# 16. Chapter B2.C12 — Budget & Financial Semantic Model

## Objective

Ensure narrative and numbers share a structured domain rather than letting the LLM improvise arithmetic.

## Budget concepts

```text
Budget
BudgetVersion
BudgetLine
BudgetCategory
FundingSource
MatchContribution
InKindContribution
CostShare
Period
Assumption
```

## Monetary rules

- decimal/fixed-point only;
- explicit currency;
- explicit period;
- deterministic totals;
- amount source/assumption lineage;
- no float arithmetic for canonical money.

## Narrative linkage

Budget lines may link to:

- project activity;
- outcome;
- proposal section;
- requirement;
- evidence/assumption.

## Tests

- totals reconcile;
- requested amount ≤ applicable ceiling where rule exists;
- match/cost share calculation deterministic;
- narrative amount mismatch detected;
- currency mismatch rejected.

---

# 17. Chapter B2.C13 — Artifact & Document Family Model

## Objective

Represent the client's complete Phase 1 document suite coherently.

## Artifact root

Common concepts:

```text
artifact_id
artifact_type
application_project_id?
logical_name
status
current_version_ref
created_by
created_at
```

## ArtifactVersion

Immutable authored/exported version with content/hash/format/generation lineage.

## Required Phase 1 families

### GrantProposal

Funder/opportunity-specific response artifact.

### BusinessPlan

Distinct business-operating artifact.

### PitchDeck

Presentation artifact derived from approved/canonical facts and project framing.

### FinancialPackage

Budget/financial outputs where required.

### PartnershipMaterial

Letters/partnership evidence or placeholders only when supported.

### TestimonialMaterial

Verified testimonial/support content only; never synthetic testimonial presented as real.

### GoalSheet

Structured milestones/outcomes/goals.

### ResearchReport

Client-visible grant/funder/winner/community research.

### QAReport

Coverage/factuality/alignment/consistency findings.

### SubmissionPackage

Bundle/manifest of submission-ready artifacts; Phase 1 may prepare but not submit.

## Tests

- artifact family coverage equals client Phase 1 scope;
- version history immutable;
- final package cannot include superseded artifact version accidentally;
- mock artifact visibly distinguishable from approved/submission-ready artifact.

## Commit

`G0-B2-C10-C13: define eligibility, requirement, budget and document production ontology`

---

# 18. Chapter B2.C14 — Outcome & Learning Feedback Ontology

## Objective

Prepare the domain for later tracking/self-improvement without building tracking now.

## OutcomeFeedback

Minimum concepts:

```text
outcome_id
application_project_id?
award_id?
outcome_type
observed_at
verified_at?
source/evidence refs
reason_codes?
freeform_feedback?
```

## Outcome types

- SUBMITTED;
- AWARDED;
- REJECTED;
- WITHDRAWN;
- REVISION_REQUESTED;
- NOT_SUBMITTED;
- UNKNOWN.

Phase 1 does not require submission automation, but the domain must not require a redesign to learn later from outcomes.

## Learning rule

Outcome does not automatically rewrite prompts/policies. It becomes evidence for Book 7/self-improvement evaluation.

## Tests

- historical award can exist without ApplicationProject;
- outcome can be linked later;
- rejection feedback preserved without becoming automatic doctrine.

---

# 19. Chapter B2.C15 — CommonGrants Interoperability Contract

## Objective

Provide standards compatibility while retaining richer internal semantics.

## Scope

Map internal domain to CommonGrants concepts for:

- Opportunity;
- Application;
- Award.

The implementation agent must use the actual pinned CommonGrants schemas/SDK version selected by the project rather than relying on memory of the standard.

## Mapping classifications

Every mapped field receives exactly one:

```text
EXACT
EXTENSION
INTERNAL_ONLY
EXTERNAL_ONLY
LOSSY
```

## Required mapping matrix columns

```text
internal_entity
internal_field
common_grants_entity
common_grants_field
mapping_class
transform
reverse_transform
loss_notes
validation
example
```

## Internal extension namespace

Define a project-owned namespace for fields CommonGrants does not represent, such as:

- evidence lineage;
- eligibility decision trace;
- match explanation;
- application workflow state;
- artifact lineage;
- client review;
- QA status;
- outcome-learning metadata.

## Round-trip rule

Where mapping is classified EXACT, internal→CommonGrants→internal must preserve semantic equality.

Where mapping is LOSSY, the loss must be explicit and test-visible.

## No shadow semantics

Do not create two competing internal fields simply to mirror an external field name. Map external semantics into the canonical internal concept.

## Tests

- Opportunity round trip;
- Application round trip;
- Award round trip;
- extension preservation;
- lossy-field reporting;
- unknown extension handling;
- schema-version mismatch;
- external ID mapping without replacing internal identity.

## Commit

`G0-B2-C14-C15: define outcome model and CommonGrants interoperability contract`

---

# 20. Chapter B2.C16 — Extension Namespace & Sector Portability

## Objective

Keep the grant ontology precise while preventing it from becoming a dead end for later Financial Literacy Framework sectors.

## Rules

1. Grant-specific concepts remain in grant namespace.
2. Cross-sector primitives may later move to platform namespace only through explicit ADR.
3. Do not prematurely generalize `GrantOpportunity` into meaningless `OpportunityObject`.
4. Organization, Person, Artifact, EvidenceClaim, CanonicalFact and StatisticObservation are candidates for shared platform primitives, but Book 2 should define them from grant requirements first.
5. Provider-specific fields live in namespaced extensions, not arbitrary root-schema pollution.

## Test

Adding a future state/private grant provider should not require changing core identity semantics.

---

# 21. Chapter B2.C17 — Georgia + Federal Fixture Architecture

## Objective

Ground the ontology in realistic first-client data shapes before Book 3 builds source governance.

## Federal fixture classes

At minimum model representative objects from:

- Grants.gov/Simpler opportunity;
- SAM/Assistance Listing;
- USAspending award;
- IRS/FAC organization/financial identity where applicable;
- Census/ACS or SAIPE statistic context.

## Georgia fixture classes

At minimum model representative objects from:

- Georgia OPB / Georgia Grants Portal opportunity/program;
- Georgia awarded-grant record where available;
- Georgia DCA or another agency-specific opportunity;
- one Georgia-specific identifier/field extension if encountered.

## Fixture rule

Book 2 fixtures are semantic examples, not live adapters. Book 3 governs SourceRegistry/Snapshot and G1 builds ingestion.

## Required scenarios

### Scenario GA-1 — Georgia nonprofit pursuing state opportunity

Represent:

- Organization;
- verified/claimed identifiers;
- Georgia opportunity/revision;
- eligibility rules;
- requirements;
- ApplicationProject;
- proposal/business-plan artifacts.

### Scenario FED-1 — Federal opportunity with assistance listing

Represent Program→Opportunity→Revision and exact eligibility/application relationships.

### Scenario AWARD-1 — Historical winner intelligence

Represent funder/program/opportunity if known, recipient Organization, Award, amount and source IDs.

### Scenario COMMUNITY-1 — Georgia community statistic

Represent geography/population/reference-period semantics without flattening to a generic number.

## Tests

Every scenario validates against domain schemas and relationship/state invariants.

## Commit

`G0-B2-C16-C17: prove extension and Georgia-federal fixture architecture`

---

# 22. Chapter B2.C18 — Client Vision Coverage Matrix

## Objective

Prove the ontology can represent the product the client asked for.

## Required coverage

### Intake

Can represent:

- organization identity;
- founder/contact;
- business concept;
- mission/vision;
- goals;
- target population;
- geography;
- program/project concept;
- financial assumptions;
- existing partnerships/evidence.

### Research & matching

Can represent:

- opportunity;
- funder;
- program;
- historical awards/winners;
- eligibility rules/decision;
- match explanation;
- research evidence;
- community statistics.

### Document generation

Can represent:

- proposal;
- business plan;
- pitch deck;
- financials;
- partnership/testimonial material;
- goal sheets;
- research reports.

### Quality

Can represent:

- requirement coverage;
- factuality evidence;
- cross-document consistency;
- alignment;
- QA reports;
- review state.

### Submission-ready output

Can represent a package and readiness state without representing that the platform actually submitted it.

## Eight grant categories

Ontology must not hard-code only federal/state grants. It must support the client's categories through funding/opportunity metadata and extensible source/provider semantics without eight separate opportunity entity types.

## Test format

```yaml
client_requirement_id:
domain_entities:
relationships:
state_machine_support:
external_mapping_if_any:
covered: true|false
gap:
```

Any uncovered Phase 1 requirement blocks Book 2 ratification.

---

# 23. Chapter B2.C19 — D0 Shadow Draft Readiness Contract

## Objective

Ensure Book 2 contributes directly to the early mock-grant milestone after Book 3.

Book 2 does **not** build the drafting harness. It defines the minimum domain bundle the D0 harness must consume.

## DraftContextBundle

Conceptual contract:

```text
Organization
+ Organization/project CanonicalFacts
+ GrantOpportunity
+ exact OpportunityRevision
+ EligibilityDecision
+ normalized Requirements
+ Funder/Program context
+ EvidenceClaims / CanonicalFacts
+ StatisticObservations
+ Budget/financial assumptions
+ Research findings
+ Proposal template/profile
→ DraftContextBundle
```

## D0 rules

- exact opportunity revision required;
- eligibility cannot be INELIGIBLE;
- mandatory unresolved eligibility may mark mock as incomplete;
- unsupported facts cannot be silently filled;
- mock proposal links each material factual assertion to evidence where practical;
- output Artifact state = DRAFT/MOCK;
- no submission state/capability.

## Readiness fixture

Create a schema-valid synthetic/manual Georgia-first DraftContextBundle that Book 3 can later replace with source-governed snapshots.

## Tests

- missing opportunity revision → fail;
- mismatched eligibility revision → fail;
- missing mandatory requirement list → fail/explicit incomplete state;
- unsupported organization fact → flagged;
- proposal and business plan contexts remain distinguishable.

---

# 24. Chapter B2.C20 — Adversarial Domain Test Suite

## Objective

Attack the ontology before Book 3/data adapters depend on it.

## A1 — Same name, different organization

Two Georgia nonprofits share nearly identical names but different verified EINs.

Expected: no silent merge.

## A2 — Rename, same organization

Legal rename with same verified identity.

Expected: same Organization.

## A3 — Source disagreement on name/address

Expected: claims coexist; identity not destroyed.

## A4 — Opportunity amendment after drafting

Expected: new OpportunityRevision; old draft retains old revision; dependency marked stale.

## A5 — Reissued opportunity number ambiguity

Expected: explicit resolution rule, no accidental merge.

## A6 — Historical award with no known opportunity

Expected: Award remains representable.

## A7 — Recipient also funder elsewhere

Expected: same Organization, different roles.

## A8 — Requirement vs proposal section confusion

Expected: separate objects linked through satisfaction relationship.

## A9 — User claim treated as verified fact

Expected: prohibited without promotion/evidence semantics.

## A10 — County statistic used as city statistic

Expected: geography mismatch detectable.

## A11 — Proposal/business plan collapse

Expected: distinct artifact types/section semantics.

## A12 — Synthetic testimonial

Expected: cannot be modeled as verified testimonial/support evidence without source/status.

## A13 — CommonGrants lossy round trip

Expected: explicit loss report, not silent truncation.

## A14 — Provider ID collision

Same string from two namespaces.

Expected: distinct identifiers.

## A15 — Cross-tenant relationship

Expected: rejected by domain validator/policy integration.

## A16 — Floating money

Expected: schema/validator rejection for canonical monetary arithmetic representation.

## A17 — Impossible state jump

IDEA→SUBMISSION_READY with no eligibility/requirements/QA.

Expected: reject.

## A18 — Stale eligibility

Eligibility evaluated against Revision 1, application now targets Revision 2.

Expected: stale/incompatible.

## A19 — Artifact uses superseded fact

Expected: traceable and QA/invalidation detectable.

## A20 — Agent invents new root entity

Worker emits `GrantWinnerCompany` instead of Organization+Award relationship.

Expected: unknown domain type rejected or extension review required.

---

# 25. Chapter B2.C21 — Book Integration & Property Tests

## Mandatory invariants

```text
1. Every root entity has stable internal identity.
2. Every external identifier is namespaced.
3. Provider IDs never replace internal primary identity.
4. Funder/Recipient/Applicant are role semantics, not duplicate organizations.
5. Opportunity revisions are immutable.
6. Eligibility decisions target exact opportunity revision.
7. ApplicationProject targets exact opportunity revision.
8. Material opportunity changes invalidate dependent decisions.
9. EvidenceClaim cannot silently become CanonicalFact.
10. Conflicting claims may coexist.
11. Statistics preserve geography/population/time context.
12. Proposal and BusinessPlan are distinct artifacts.
13. Requirement and RequirementResponse are distinct.
14. Artifact and SourceSnapshot are distinct semantic types.
15. Historical Award can exist without internal ApplicationProject.
16. Money uses decimal/fixed-point semantics.
17. State transitions are enumerated and validated.
18. Submission-ready does not imply submitted.
19. CommonGrants mappings report loss explicitly.
20. Every Phase 1 client requirement is representable.
21. Georgia and federal fixtures validate against the same core ontology.
22. D0 DraftContextBundle is representable without agent memory.
```

## Property tests

Where practical:

- serialize→deserialize preserves semantic equality;
- EXACT CommonGrants mapping round-trip preserves equality;
- revision history append does not mutate previous revision;
- identifiers normalize idempotently;
- deterministic state transition validator returns same result for same inputs.

---

# 26. Chapter B2.C22 — Book 2 Reality Lock

## Machine-readable report

```json
{
  "book": "G0-B2",
  "status": "PASS|FAIL",
  "glossary_complete": true,
  "entity_boundaries_ratified": true,
  "root_entities_with_stable_identity": 1.0,
  "external_ids_namespaced": true,
  "relationship_catalog_complete": true,
  "state_machine_tests_pass": true,
  "revision_replay_tests_pass": true,
  "fact_claim_evidence_tests_pass": true,
  "eligibility_determinism_contract_pass": true,
  "application_document_model_pass": true,
  "common_grants_exact_roundtrip_pass": true,
  "common_grants_loss_reporting_pass": true,
  "client_phase1_domain_coverage": 1.0,
  "georgia_federal_fixture_tests_pass": true,
  "d0_draft_context_ready": true,
  "adversarial_p0_pass": true,
  "p0_open": 0,
  "ready_for_book3": true
}
```

`ready_for_book3` is computed from evidence and must be false if any required predicate fails.

---

# 27. Commit Plan

The execution agent should work continuously and checkpoint at coherent semantic boundaries:

```text
1. G0-B2-C1
   glossary / ubiquitous language

2. G0-B2-C2
   entity boundary ADRs

3. G0-B2-C3
   core entity catalog

4. G0-B2-C4-C5
   identity + external identifier semantics

5. G0-B2-C6
   relationship catalog

6. G0-B2-C7
   state machines

7. G0-B2-C8-C9
   revisions + fact/claim/evidence semantics

8. G0-B2-C10-C13
   eligibility + requirements + budget + artifact/document ontology

9. G0-B2-C14-C15
   outcomes + CommonGrants interoperability

10. G0-B2-C16-C17
    extension policy + Georgia/federal fixtures

11. G0-B2-C18-C19
    client coverage + D0 draft readiness

12. G0-B2-C20-C21
    adversarial + integration/property tests

13. G0-B2-BOOK
    complete Book 2 implementation/evidence packet

14. G0-B2-REPAIR-1...N
    bounded review repairs

15. G0-B2-RATIFY
    pass Book 2 Reality Lock
```

The agent should not wait for approval between commits unless it discovers:

- P0 contradiction with Book 1;
- irreconcilable ambiguity in client scope;
- external-standard behavior requiring a material architecture choice not covered by ADR authority;
- licensing/security blocker affecting ontology dependency.

---

# 28. Parallel-Agent Work Allocation

Because multiple agents may work simultaneously, Book 2 can be parallelized **inside controlled boundaries**.

## Lane A — Domain Core

Owns:

- C1 glossary;
- C2 boundaries;
- C3 entity catalog.

This lane lands first because others depend on it.

## Lane B — Identity & Lifecycle

After C2 boundary freeze:

- C4 identity;
- C5 identifiers;
- C6 relationships;
- C7 states;
- C8 revision semantics.

## Lane C — Application Production Ontology

After C3 core catalog:

- C10 eligibility;
- C11 requirements/content;
- C12 budget;
- C13 artifacts;
- C14 outcomes.

## Lane D — Interoperability

After C2/C3:

- inspect/pin actual CommonGrants schema version;
- C15 mapping;
- C16 extension policy.

## Lane E — Fixtures & Tests

After schemas stabilize:

- C17 Georgia/federal fixtures;
- C18 coverage;
- C19 D0 readiness;
- C20/C21 tests.

## Merge rule

No lane may independently redefine a core entity boundary. Changes route through the Book 2 ADR register and Domain Core owner.

This prevents parallel agents from creating five subtly incompatible ontologies.

---

# 29. Allowed / Prohibited Paths

## Allowed

- Book 2 documentation;
- domain schemas/config;
- bounded domain prototypes/validators;
- fixtures/tests;
- CommonGrants mapping prototype;
- Book 2 ADRs/evidence.

## Prohibited

- production source adapters (Book 3/G1);
- production database migrations beyond disposable schema prototype;
- Hermes memory implementation (Book 4);
- final evidence backend choice (Book 5);
- production auth/tool gateway (Book 6);
- production drafting application (later G1; D0 contract only here);
- external submission;
- trading/OCE unrelated code;
- changing Book 1 authority without amendment.

---

# 30. Definition of Done

Book 2 is complete only when:

1. one canonical domain glossary exists;
2. all high-cost entity boundaries have ADRs;
3. core entity catalog is complete;
4. identity semantics survive rename/source disagreement;
5. external IDs are fully namespaced;
6. relationship semantics are typed;
7. state transitions are explicit/tested;
8. opportunity/application revision history is replayable;
9. facts/claims/statistics are semantically distinct;
10. eligibility has a deterministic evaluation contract;
11. requirements and their responses are distinct;
12. budget arithmetic semantics are deterministic;
13. the full client document suite is representable;
14. historical outcomes/awards support later learning;
15. CommonGrants mapping is pinned, classified and loss-aware;
16. Georgia and federal fixtures share the same core ontology;
17. all client Phase 1 requirements have domain coverage;
18. a D0 DraftContextBundle can be built without hidden agent memory;
19. adversarial P0 cases pass;
20. Reality Lock reports zero open P0 and `ready_for_book3=true`.

---

# 31. Precise Handoff to Book 3

Book 3 receives **meaning**, not implementation guesswork.

Book 2 hands off:

```text
ENTITY TYPES
IDENTITY RULES
EXTERNAL-ID NAMESPACES
RELATIONSHIP TYPES
STATE MACHINES
REVISION SEMANTICS
FACT / CLAIM / STATISTIC SHAPES
ELIGIBILITY RULE SHAPE
REQUIREMENT MODEL
APPLICATION / ARTIFACT MODEL
COMMON GRANTS MAPPING
GEORGIA/FEDERAL SEMANTIC FIXTURES
D0 DRAFT CONTEXT CONTRACT
```

Book 3 then answers:

> How does outside reality enter these semantic objects, how is it snapshotted, ranked by authority, aged, refreshed, conflicted, revised, promoted and retained?

Book 3 must not redefine what Organization, OpportunityRevision, EvidenceClaim or StatisticObservation mean merely because a source adapter exposes inconvenient fields.

If a source does not fit, the adapter maps it or an explicit Book 2 amendment is proposed.

---

# 32. Book 2 North-Star Test

At the end of Book 2, we should be able to hand the same typed domain packet to:

- a human reviewer;
- CEO Hermes;
- a deterministic eligibility service;
- a grant-writing worker;
- a CommonGrants exporter;
- a future web UI;
- a future evidence backend;

and all of them should agree on **what every object is, which exact version it represents, how it is related, and what it is allowed to mean**.

If that is not true, Book 2 is not finished.