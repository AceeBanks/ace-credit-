# G0 Block 00–03 Master Implementation Plan

**Document ID:** GS-G0-B00-03-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR EXECUTION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-24

---

# 0. Mission

G0.0–G0.3 converts R0 discovery into the binding constitutional and data architecture required before implementation begins.

This block is not a coding sprint in the ordinary sense. It is a **design-control and contract-freeze phase**. The objective is to eliminate architectural ambiguity before the clean production repository is created.

The output of G0.0–G0.3 must make it possible for an implementation team or autonomous coding agent to build the first production-shaped vertical slice without inventing authority rules, data semantics, source precedence, domain identities, provenance behavior, or compatibility mappings during coding.

The block contains four chapters:

- **G0.0 — R0 Ratification & Reality Lock**
- **G0.1 — Product Constitution & Authority Model**
- **G0.2 — Grant Domain Ontology & CommonGrants Mapping**
- **G0.3 — Grant Intelligence Data Constitution**

G0.4+ may not redefine any G0.0–G0.3 invariant without an explicit ADR/supersession record.

---

# 1. Governing Build Philosophy

## 1.1 Constitution before implementation

No subsystem may be implemented merely because a suitable library exists.

Every subsystem must first have:

- an authority owner;
- a canonical data contract;
- explicit input/output boundaries;
- a source-of-truth rule;
- provenance expectations;
- failure semantics;
- validation tests;
- an observability/audit surface;
- a migration/versioning policy.

## 1.2 Deterministic questions remain deterministic

LLMs may assist with extraction, interpretation, summarization, synthesis, and ambiguous reasoning.

LLMs do not become authoritative for:

- eligibility once rules are normalized;
- monetary arithmetic;
- dates/deadlines;
- source identity;
- canonical identifiers;
- requirement completion state;
- policy authorization;
- database truth;
- provenance lineage.

## 1.3 Evidence before promotion

External facts do not become canonical because an agent stated them.

A promoted external fact must have:

- source identity;
- immutable source snapshot;
- retrieval time;
- extraction method/version;
- confidence/status;
- contradiction state;
- freshness semantics;
- relationship to canonical entities.

## 1.4 Feed-forward over context accumulation

The architecture must favor bounded typed packets over raw-context propagation.

This principle already governs Personal Hermes → CEO Hermes → specialist workers and must also govern source ingestion and downstream generation.

## 1.5 Interoperable internal richness

Where CommonGrants provides public standards for Opportunity, Application, and Award models, the product should support explicit mapping while retaining richer internal fields needed for evidence, matching, eligibility, workflow, audit, and client experience.

---

# 2. Block-Level Success Definition

G0.0–G0.3 succeeds when:

1. R0 findings are frozen into a signed/ratified authority packet.
2. Every role/system has explicit authority and prohibited actions.
3. Core Grant-domain entities are defined with stable identities and relationships.
4. CommonGrants compatibility is mapped and testable.
5. Source ingestion is governed by a single Source Registry and immutable Source Snapshot model.
6. External identifiers have deterministic namespace/validation rules.
7. quantitative evidence uses a typed `StatisticObservation` contract.
8. source precedence, freshness, revisions, contradictions, and promotion rules are explicit.
9. no implementation team needs to invent basic data semantics during G1.
10. a G0.0–G0.3 Reality Lock produces PASS before G0.4 begins.

---

# 3. Master Deliverable Tree

```text
docs/grant-sector/g0/
├── 00-ratification/
│   ├── G0_0_R0_RATIFICATION_PACKET.md
│   ├── G0_0_DECISION_REGISTER.md
│   ├── G0_0_NON_GOALS.md
│   ├── G0_0_PROTOTYPE_CANDIDATE_REGISTER.md
│   └── G0_0_REALITY_LOCK_REPORT.md
│
├── 01-constitution/
│   ├── G0_1_PRODUCT_CONSTITUTION.md
│   ├── G0_1_AUTHORITY_MATRIX.md
│   ├── G0_1_CAPABILITY_LADDER.md
│   ├── G0_1_HUMAN_APPROVAL_POLICY.md
│   ├── G0_1_SELF_IMPROVEMENT_GOVERNANCE.md
│   └── G0_1_CONSTITUTION_TEST_REPORT.md
│
├── 02-domain/
│   ├── G0_2_DOMAIN_ONTOLOGY.md
│   ├── G0_2_ENTITY_IDENTITY_RULES.md
│   ├── G0_2_RELATIONSHIP_CATALOG.md
│   ├── G0_2_COMMON_GRANTS_MAPPING.md
│   ├── G0_2_JSON_SCHEMA_DRAFTS/
│   ├── G0_2_DOMAIN_INVARIANTS.md
│   └── G0_2_DOMAIN_TEST_REPORT.md
│
├── 03-data/
│   ├── G0_3_DATA_CONSTITUTION.md
│   ├── G0_3_SOURCE_REGISTRY_SCHEMA.md
│   ├── G0_3_SOURCE_SNAPSHOT_SCHEMA.md
│   ├── G0_3_EXTERNAL_IDENTIFIER_SCHEMA.md
│   ├── G0_3_STATISTIC_OBSERVATION_SCHEMA.md
│   ├── G0_3_SOURCE_PRECEDENCE_MATRIX.md
│   ├── G0_3_FRESHNESS_POLICY.md
│   ├── G0_3_REVISION_CHANGE_PROTOCOL.md
│   ├── G0_3_CONFLICT_RESOLUTION_PROTOCOL.md
│   ├── G0_3_DATA_RETENTION_POLICY.md
│   ├── G0_3_PROVENANCE_REQUIREMENTS.md
│   └── G0_3_DATA_CONSTITUTION_TEST_REPORT.md
│
└── G0_0_TO_3_RATIFICATION_SUMMARY.md
```

The exact path may change during repo creation, but the deliverable classes are binding.

---

# 4. G0.0 — R0 Ratification & Reality Lock

## 4.1 Objective

Convert all R0 exploratory findings into a finite, versioned set of accepted, rejected, deferred, and unresolved decisions.

R0 discovered many potentially reusable components and architectural patterns. G0.0 prevents those discoveries from remaining informal suggestions.

The central question is:

> **What from R0 is now allowed to influence the production architecture?**

---

## 4.2 Inputs

Mandatory inputs:

- Dual-Hermes Context & R0 Charter;
- R0 Salvage Map;
- R0 Branch Archaeology Notes;
- R0 Reject / Do-Not-Port Ledger;
- R0 Gap Map;
- R0 Seed Architecture Recommendation;
- R0 Grant Domain Data Source Deep Hunt;
- R0 External Repo Review Batch 01;
- Semantica/Treg review;
- Awesome AI Apps classification;
- existing OCE constitutional/Block 1 doctrine;
- G0 Entry Plan.

All inputs must be referenced by file and commit SHA where practical.

---

## 4.3 Chapter Structure

### G0.0.C1 — Evidence inventory

Create a manifest of all R0 evidence.

Fields:

```yaml
artifact_id:
path:
commit_sha:
artifact_type:
authority_level:
status:
supersedes:
superseded_by:
notes:
```

Purpose:

- stop accidental reliance on stale versions;
- preserve lineage;
- establish what is authoritative for G0.

### G0.0.C2 — Decision normalization

Every R0 conclusion gets one status:

- RATIFIED;
- RATIFIED_WITH_CONDITION;
- PROTOTYPE_REQUIRED;
- DEFERRED;
- REJECTED;
- UNRESOLVED.

Examples:

```text
Dual-Hermes split                  RATIFIED
Postgres authoritative truth      RATIFIED
Redis non-authoritative transport RATIFIED
Semantica evidence substrate      PROTOTYPE_REQUIRED
Crawl4AI web extraction           PROTOTYPE_REQUIRED
Treg code embedding               REJECTED pending license
Treg architecture pattern         RATIFIED_WITH_CONDITION
Candid paid dependency            DEFERRED
```

### G0.0.C3 — Contradiction sweep

Search for contradictory architectural statements across R0 docs.

Classes:

- authority contradiction;
- data ownership contradiction;
- storage contradiction;
- component disposition contradiction;
- source-precedence contradiction;
- security contradiction;
- naming/schema contradiction;
- implementation timing contradiction.

Every contradiction becomes a record:

```yaml
contradiction_id:
claim_a:
claim_b:
source_a:
source_b:
severity: P0|P1|P2
resolution:
authority:
status:
```

No P0 may remain unresolved.

### G0.0.C4 — Non-goal freeze

Explicitly list what G0/G1 does not attempt.

Initial non-goals:

- autonomous submission;
- 50-state grant coverage;
- complete private-foundation coverage;
- generic agent OS development;
- worker long-term autobiographical memory;
- Kubernetes;
- universal ontology;
- autonomous code deployment by CEO Hermes;
- Candid dependency in first vertical slice;
- graph database unless Semantica bake-off proves need;
- direct Hermes database access.

### G0.0.C5 — Prototype candidate freeze

Freeze exactly which technologies require bake-off rather than architectural debate.

Initial candidates:

- Semantica vs product-owned relational evidence substrate;
- Unstructured vs salvaged parser stack;
- PixelRAG visual fallback;
- Crawl4AI source extraction;
- GPT Researcher bounded research patterns;
- Promptfoo + Hermes Eval Lab;
- Univer spreadsheet workspace;
- Activepieces bounded integration layer.

Each candidate needs:

- hypothesis;
- competing baseline;
- success metrics;
- kill criteria;
- target G0/G1 chapter.

---

## 4.4 Implementation Work

G0.0 code work is limited to **verification utilities**, not product implementation.

Recommended utilities:

```text
tools/g0/
  build_artifact_manifest.py
  scan_doc_conflicts.py
  validate_decision_register.py
  check_r0_links.py
  generate_ratification_digest.py
```

These scripts should:

- verify referenced files exist;
- verify commit/path identity;
- ensure no duplicate decision IDs;
- ensure all unresolved P0 decisions are visible;
- fail CI if a required ratification artifact is missing.

---

## 4.5 G0.0 Test Plan

### Structural tests

- all required R0 files present;
- every ratified decision has an ID;
- every prototype candidate has owner/status/exit criteria;
- all non-goals explicitly versioned;
- no orphaned contradiction records.

### Consistency tests

Assertions:

```text
Personal Hermes != CEO Hermes identity
Hermes != canonical truth
Postgres == authoritative operational state
Redis != authoritative accepted job state
Workers == bounded/non-sovereign
Deterministic eligibility != LLM final decision
Secrets != memory/logs/Git
```

### Adversarial tests

Inject deliberately contradictory claims into a test fixture and verify the ratification validator refuses PASS.

Examples:

- one file says CEO can submit grants at L2;
- another says submission is L5;
- one file says Redis queue is authoritative;
- another says Postgres is authoritative.

Reality Lock must fail.

---

## 4.6 Deliverables

Required:

1. `G0_0_R0_RATIFICATION_PACKET.md`
2. `G0_0_DECISION_REGISTER.md`
3. `G0_0_NON_GOALS.md`
4. `G0_0_PROTOTYPE_CANDIDATE_REGISTER.md`
5. `G0_0_REALITY_LOCK_REPORT.md`
6. machine-readable decision register (`json`/`yaml`)
7. CI ratification check.

---

## 4.7 Exit Gate

**PASS only if:**

- zero unresolved P0 contradictions;
- every R0 recommendation has disposition;
- production boundary is explicit;
- prototype candidates are bounded;
- no stale artifact is silently authoritative;
- reality-lock validator passes.

Failure means G0.1 does not begin.

---

# 5. G0.1 — Product Constitution & Authority Model

## 5.1 Objective

Define who or what may observe, propose, decide, mutate, approve, and execute every class of product action.

The constitution must remain valid if models, providers, workers, UI, or libraries change.

---

## 5.2 Constitutional Actors

At minimum:

- Human Client/User;
- Human Admin/Operator;
- Personal Hermes;
- CEO Hermes;
- Specialist Worker Agent;
- Deterministic Domain Service;
- Source Adapter;
- Policy Engine;
- Canonical Database;
- Artifact Store;
- External Integration;
- Future Outreach Agent;
- Future Submission Agent.

Each actor receives an immutable actor type and explicit capabilities.

---

## 5.3 Chapter Structure

### G0.1.C1 — Constitutional laws

Binding laws should include:

**Law 1 — Canonical truth**

Hermes and worker memory are not authoritative state.

**Law 2 — Bounded authority**

Every agent acts only through capabilities explicitly granted by policy.

**Law 3 — Human consequence gate**

High-consequence external actions require explicit approval unless later policy specifically ratifies an exception.

**Law 4 — Deterministic supremacy for deterministic constraints**

Normalized eligibility, arithmetic, deadlines, identifiers, and workflow invariants are evaluated by deterministic services.

**Law 5 — Evidence promotion**

External facts require source lineage and promotion status.

**Law 6 — Agent replaceability**

Any Hermes/worker can be reset/replaced without losing canonical business state.

**Law 7 — Secrets separation**

Agents receive scoped capability, not raw durable credentials.

**Law 8 — No silent self-modification**

Prompts, skills, policies, code, and source adapters require evaluated promotion.

**Law 9 — Auditability**

Consequential actions require actor, capability, target, timestamp, request ID, result, and evidence/approval references.

**Law 10 — Fail closed**

Missing authority, missing required evidence, unknown policy, schema invalidity, or ambiguous tenant scope blocks action.

### G0.1.C2 — Authority ladder

Freeze L0–L5:

```text
L0 OBSERVE
Read authorized state/evidence only.

L1 PROPOSE
Create plans/recommendations/draft intents but cannot mutate governed project state.

L2 SAFE EXECUTE
Perform bounded research, parsing, matching computation, draft generation, QA and internal artifact creation.

L3 MANAGED EXECUTE
Mutate governed internal application/project state under policy and full audit.

L4 EXTERNAL ACTION
Send externally visible communications, outreach, integrations or data updates after policy/human approval.

L5 SUBMISSION / LEGALLY MATERIAL ACTION
Submit grant applications, bind attestations, sign/certify, or perform equivalent high-consequence action.
```

Initial phase policy:

- Personal Hermes: L0–L1 normally;
- CEO Hermes: L0–L2, narrowly selected L3 later;
- specialist workers: task-scoped L0/L2 only;
- deterministic services: narrow system-defined mutations;
- L4/L5 unavailable until future ratification.

### G0.1.C3 — Capability model

Define typed capabilities instead of arbitrary tool permissions.

Examples:

```text
organization.read
organization.propose_update
opportunity.search
opportunity.ingest
eligibility.evaluate
match.rank
research.funder
research.winner
research.community
source.fetch
source.snapshot
application.draft
application.update_internal
artifact.generate
qa.run
email.propose
email.send
submission.prepare
submission.execute
```

Each capability contract includes:

- actor types allowed;
- minimum authority level;
- input schema;
- target/resource scope;
- approval policy;
- side effects;
- audit requirements;
- reversibility;
- rate limits;
- failure semantics.

### G0.1.C4 — Human approval policy

Classify actions:

- no approval;
- review-after;
- approval-before;
- dual approval;
- permanently prohibited in current phase.

Examples:

```text
search grant source           no approval
create draft proposal         no approval
change canonical org profile  approval-before if client-provided conflict
send outreach email           approval-before
submit grant                  prohibited until L5 enabled
```

### G0.1.C5 — Self-improvement governance

Freeze lifecycle:

```text
Observation
 ↓
Candidate lesson
 ↓
Candidate change
 ↓
Sandbox / eval corpus
 ↓
Baseline vs candidate
 ↓
Human/policy review
 ↓
PROMOTE | REVISE | REJECT
 ↓
Versioned rollout
 ↓
Rollback monitor
```

CEO Hermes may propose changes; it cannot silently promote them.

### G0.1.C6 — Failure and escalation law

Define behavior for:

- missing authority;
- ambiguous tenant;
- missing source;
- conflicting source;
- source outage;
- model outage;
- worker timeout;
- invalid result;
- budget inconsistency;
- deadline uncertainty;
- external tool failure.

Required pattern:

```text
FAIL_CLOSED
or
DEGRADE_TO_READ_ONLY
or
ESCALATE_HUMAN
```

Never improvise authority.

---

## 5.4 Implementation Work

Create machine-readable authority artifacts:

```text
schemas/policy/actor.schema.json
schemas/policy/capability.schema.json
schemas/policy/authority_grant.schema.json
schemas/policy/approval_policy.schema.json
config/policy/capability_registry.yaml
config/policy/authority_matrix.yaml
```

Prototype a policy evaluator stub:

```python
decide(actor, capability, resource, tenant, context) ->
ALLOW | DENY | REQUIRE_APPROVAL
```

The stub does not need production auth integration yet. It must prove that constitution rules are executable rather than prose-only.

---

## 5.5 G0.1 Test Plan

### Authority matrix tests

- Personal Hermes cannot use CEO-only capability.
- worker cannot escalate itself to L3.
- CEO cannot submit at L2.
- source adapter cannot mutate OrganizationProfile.
- deterministic service cannot bypass tenant scope.

### Fail-closed tests

- unknown capability → DENY;
- unknown actor → DENY;
- missing tenant → DENY;
- expired authority grant → DENY;
- conflicting approval status → DENY;
- malformed target scope → DENY.

### Positive tests

- CEO research request at L2 → ALLOW;
- worker source fetch inside assigned task → ALLOW;
- proposal draft generation inside assigned application → ALLOW.

### Human approval tests

- profile canonical fact replacement triggers approval when required;
- external email send returns REQUIRE_APPROVAL;
- submission action remains DENY even if worker attempts it.

### Constitutional mutation tests

Any change to L0–L5 semantics or capability ownership must require an ADR identifier in CI.

---

## 5.6 Deliverables

1. Product Constitution;
2. Actor Catalog;
3. Authority Matrix;
4. Capability Registry;
5. L0–L5 ladder specification;
6. Human Approval Matrix;
7. Self-Improvement Governance;
8. Failure/Escalation Matrix;
9. machine-readable policy schemas/config;
10. constitution test report.

---

## 5.7 Exit Gate

PASS when every consequential operation class has:

- actor owner;
- capability;
- authority level;
- tenant/resource scope;
- approval requirement;
- audit requirement;
- fail-closed behavior.

No “agent can do whatever the tool allows” path may exist.

---

# 6. G0.2 — Grant Domain Ontology & CommonGrants Mapping

## 6.1 Objective

Define the canonical language of the product.

Every later service, database table, API, Hermes packet, evidence relationship, source adapter, and application artifact must refer to the same entity identities and relationship semantics.

---

## 6.2 Core Entity Set

### Organization

Represents applicant, recipient, funder organization, partner, vendor, etc.

Key properties:

- internal `organization_id`;
- legal/display names;
- organization roles;
- addresses/geographies;
- external identifiers;
- lifecycle/status;
- canonical facts;
- source verification state.

### Person

Only where operationally required.

- person_id;
- role/relationship;
- credentials/claims with evidence;
- contact details with sensitivity policy.

### Funder

May be represented as role/subtype of Organization, but domain semantics must expose:

- issuer identity;
- funding programs;
- source systems;
- historical awards;
- priorities/research.

### Program / Assistance Listing

Represents the durable funding program beneath individual opportunities.

Important federal identifier:

- Assistance Listing Number (ALN/CFDA lineage).

### GrantOpportunity

The currently available or historical opportunity.

Must support:

- internal identity;
- issuer/program;
- external identifiers;
- title/description;
- open/close dates;
- award floor/ceiling/estimated total;
- eligibility data;
- funding categories;
- geography;
- source snapshots;
- revisions;
- requirements;
- status.

### EligibilityRule

Normalized deterministic predicate derived from source text/fields.

Fields:

```yaml
rule_id:
opportunity_id:
rule_type:
operator:
subject_field:
expected_value:
source_claim_ref:
required: true
confidence:
normalization_status:
```

### EligibilityDecision

Reproducible evaluation result:

- organization;
- opportunity;
- evaluated rule set/version;
- per-rule result;
- overall PASS/FAIL/UNKNOWN;
- evaluated_at;
- source/version references.

### Award

Historical or current funding award.

- award_id;
- opportunity/program relationship;
- funder;
- recipient;
- amount;
- dates;
- geography;
- external award identifiers;
- source snapshots.

### ApplicationProject

Internal working object for producing/submitting an application.

Must remain distinct from public-standard Application representation where our workflow requires richer internal state.

### Requirement

A concrete solicitation/application requirement.

- response/attachment/certification/budget/eligibility/etc.;
- required/optional;
- due/status;
- source lineage;
- satisfaction evidence.

### Budget

Canonical structured budget data separate from rendered XLSX/PDF.

### CanonicalFact

Product-owned normalized fact about an organization, opportunity, project, or application.

State labels:

- CLIENT_PROVIDED;
- VERIFIED_OFFICIAL;
- DERIVED;
- INFERRED;
- STALE;
- CONFLICTED.

### EvidenceClaim

Specific claim tied to source and used by applications/research.

### StatisticObservation

Typed quantitative observation with geography, vintage, measure and provenance.

### Artifact

Versioned generated/uploaded/research output.

### OutcomeFeedback

Award/rejection/feedback event used later for learning and tracking.

---

## 6.3 Chapter Structure

### G0.2.C1 — Entity boundary decisions

Resolve:

- Funder as subtype/role of Organization vs separate root entity;
- Recipient as role of Organization vs separate entity;
- Program vs Opportunity boundary;
- public Application vs internal ApplicationProject;
- CanonicalFact vs EvidenceClaim;
- Artifact vs SourceSnapshot;
- Person contact vs Organization member identity.

Each decision gets ADR-like rationale.

### G0.2.C2 — Identity rules

Every entity must have stable internal UUID/ULID independent of source IDs.

External IDs are attached through `ExternalIdentifier`.

Identity merge rules must support:

- organization rename with same EIN;
- multiple names/DBAs;
- one program issuing many opportunities;
- one opportunity with multiple revisions;
- award IDs across USAspending/SAM/agency systems;
- one geography with FIPS plus human-readable label.

No external provider ID becomes the database primary key.

### G0.2.C3 — Relationship catalog

Define typed relations, for example:

```text
FUNDER --ISSUES--> PROGRAM
PROGRAM --PUBLISHES--> OPPORTUNITY
OPPORTUNITY --HAS_RULE--> ELIGIBILITY_RULE
ORGANIZATION --EVALUATED_FOR--> ELIGIBILITY_DECISION
ORGANIZATION --SUBMITS--> APPLICATION_PROJECT
AWARD --AWARDED_TO--> ORGANIZATION
AWARD --DERIVED_FROM--> OPPORTUNITY
CLAIM --SUPPORTED_BY--> SOURCE_SNAPSHOT
CLAIM --USED_IN--> ARTIFACT
CLAIM --CONTRADICTS--> CLAIM
STATISTIC --APPLIES_TO--> GEOGRAPHY
APPLICATION_PROJECT --USES--> CANONICAL_FACT
```

The relationship catalog becomes input to the Semantica bake-off later.

### G0.2.C4 — CommonGrants mapping

Map internal models to CommonGrants Opportunity/Application/Award.

For every field:

```yaml
internal_field:
common_grants_field:
direction: import|export|bidirectional
mapping_type: exact|transform|lossy|not_supported
notes:
```

Classification:

- EXACT;
- EXTENSION;
- INTERNAL_ONLY;
- EXTERNAL_ONLY;
- LOSSY.

The product should be able to ingest or emit CommonGrants-compatible objects without reducing internal richness.

### G0.2.C5 — Schema draft

Produce JSON Schema/Pydantic-equivalent drafts for core entities.

At minimum:

- Organization;
- GrantOpportunity;
- Program;
- EligibilityRule;
- EligibilityDecision;
- Award;
- ApplicationProject;
- Requirement;
- CanonicalFact;
- EvidenceClaim;
- Artifact;
- OutcomeFeedback.

`SourceSnapshot`, `ExternalIdentifier`, and `StatisticObservation` finalize in G0.3.

### G0.2.C6 — Domain invariants

Examples:

- opportunity must have at least one source reference;
- active opportunity with deadline must use timezone-aware date semantics;
- EligibilityDecision references exact rule-set version;
- Award recipient must resolve to canonical Organization;
- ApplicationProject cannot be its own source evidence;
- CanonicalFact state CONFLICTED cannot silently be used as VERIFIED_OFFICIAL;
- derived/inferred facts preserve parent evidence refs;
- public standard mappings cannot overwrite richer internal fields without explicit transformation record.

---

## 6.4 Implementation Work

Build a temporary `domain-contracts` package inside the planning branch or test harness.

Suggested structure:

```text
prototype/g0/domain/
  models.py
  enums.py
  identifiers.py
  common_grants.py
  invariants.py
  fixtures/
```

Purpose:

- prove schemas instantiate;
- test serialization;
- test mappings;
- test identity edge cases;
- generate JSON Schema.

This prototype is disposable if needed; the **contracts**, not prototype code, are authoritative.

---

## 6.5 G0.2 Test Plan

### Schema tests

- valid object passes;
- missing required identity fails;
- unknown enum rejected where closed vocabulary required;
- timestamps timezone-aware;
- money uses fixed/decimal representation, never floating-point ambiguity.

### Identity tests

1. nonprofit changes name but EIN stable → same Organization;
2. two organizations share similar names but distinct EIN → remain distinct;
3. opportunity revision retains canonical opportunity lineage;
4. same award appears in two sources with crosswalk IDs → one canonical Award after validated merge;
5. missing external identifier → still valid internal entity but lower verification state.

### Mapping tests

- internal → CommonGrants → internal round-trip preserves all CommonGrants-compatible fields;
- extensions remain retained internally;
- lossy mappings explicitly reported;
- unknown external fields captured in extension/metadata lane rather than dropped silently.

### Relationship tests

- invalid relation types rejected;
- relationship endpoints require allowed entity classes;
- self-contradictory relationships rejected unless explicitly modeled.

### Domain invariants tests

- conflicted fact cannot satisfy verified eligibility prerequisite;
- expired opportunity cannot enter READY_TO_APPLY without explicit override;
- application project points to exact opportunity revision.

---

## 6.6 Deliverables

1. Domain Ontology;
2. Entity Identity Rules;
3. Relationship Catalog;
4. CommonGrants Mapping Matrix;
5. core JSON Schema/Pydantic drafts;
6. Domain Invariants;
7. example fixtures;
8. mapping/roundtrip test suite;
9. domain test report.

---

## 6.7 Exit Gate

PASS when:

- no unresolved P0 ambiguity exists in core entity boundaries;
- every entity has identity semantics;
- relationships are typed;
- CommonGrants mapping is explicit/testable;
- schemas pass fixtures and invariants;
- G0.3 can build source/provenance rules without changing entity meaning.

---

# 7. G0.3 — Grant Intelligence Data Constitution

## 7.1 Objective

Define how external reality enters, changes, conflicts, ages, and becomes usable inside the platform.

This chapter is the foundation for source trust, research reproducibility, eligibility correctness, winner analysis, community evidence, and application factuality.

---

## 7.2 Core Contracts

### SourceRegistry

One row/object per configured source.

Minimum fields:

```yaml
source_id:
name:
source_class:
authority_tier:
jurisdiction:
domain:
access_mode: API|BULK|WEB|UPLOAD|MANUAL
base_url:
auth_mode:
expected_update_frequency:
default_freshness_policy:
terms_policy_ref:
robots_policy_ref:
adapter_name:
adapter_version:
health_status:
last_success_at:
last_failure_at:
enabled:
```

### SourceSnapshot

Immutable captured external state.

```yaml
snapshot_id:
source_id:
retrieved_at:
source_effective_at:
request_identity:
external_resource_id:
raw_object_uri:
raw_hash:
content_type:
adapter_version:
parser_version:
previous_snapshot_id:
revision_key:
http_metadata:
status:
```

Rule:

> never mutate a SourceSnapshot in place.

### ExternalIdentifier

```yaml
external_identifier_id:
namespace:
value:
entity_type:
entity_id:
issuer:
valid_from:
valid_to:
verification_state:
source_snapshot_id:
```

Initial namespaces:

- EIN;
- UEI;
- ALN;
- GRANTS_GOV_OPPORTUNITY_NUMBER;
- FAIN;
- USA_SPENDING_AWARD_ID;
- SAM identifiers;
- FIPS;
- state portal IDs;
- CommonGrants IDs.

### StatisticObservation

```yaml
statistic_id:
metric_code:
metric_label:
value:
unit:
geography_type:
geography_id:
geography_label:
population_scope:
reference_period_start:
reference_period_end:
dataset_name:
dataset_version:
margin_of_error:
confidence_interval:
methodology_ref:
source_snapshot_id:
retrieved_at:
quality_state:
```

### SourceChangeEvent

```yaml
change_event_id:
source_id:
entity_type:
entity_id:
old_snapshot_id:
new_snapshot_id:
change_class:
materiality:
affected_fields:
detected_at:
downstream_actions:
status:
```

---

## 7.3 Source Authority Classes

Proposed initial hierarchy:

### Tier A — Primary authoritative issuer/government record

Examples:

- current official solicitation;
- Grants.gov/Simpler opportunity record;
- SAM Assistance Listing;
- official agency/state grant portal;
- IRS official filing data;
- Census/BLS/CDC official statistics.

### Tier B — Authoritative transactional/award record

Examples:

- USAspending;
- agency award databases;
- FAC;
- SAM subaward data.

### Tier C — Trusted institutional/curated secondary

Examples:

- ProPublica nonprofit explorer;
- Candid where licensed;
- established foundation databases;
- issuer-maintained news/history pages.

### Tier D — Governed web secondary

Examples:

- funder webpage;
- partner report;
- credible research publication;
- organizational website.

### Tier E — User-provided/unverified

Examples:

- client statement;
- uploaded draft;
- manually entered claim.

Tier is not equivalent to truth; it defines precedence and verification expectations.

---

## 7.4 Chapter Structure

### G0.3.C1 — Source Registry design

Freeze source onboarding process:

```text
Candidate Source
  ↓
Terms / access / authority review
  ↓
Source Registry entry
  ↓
Adapter contract
  ↓
fixture replay
  ↓
health checks
  ↓
ENABLED
```

No unregistered source adapter can promote facts.

### G0.3.C2 — Snapshot & replay doctrine

Every external API/web/document retrieval that influences a promoted fact must produce/refer to an immutable snapshot.

Replay requirements:

- exact raw response/page/document available or content-addressed object reference preserved;
- hash verification;
- adapter/parser version recorded;
- derived facts reference snapshot;
- later adapter versions can reparse old snapshot without refetching external source.

### G0.3.C3 — Revision/change protocol

Define material changes.

Examples:

**P0 material change**

- eligibility changed;
- deadline changed;
- award amount changed;
- required attachment changed;
- applicant type/geography changed;
- opportunity cancelled.

**P1 material change**

- program description changed;
- contact details changed;
- evaluation criteria changed;
- guidance updated.

**P2 nonmaterial**

- formatting;
- typo with no semantic effect;
- navigation metadata.

P0 event triggers mandatory downstream invalidation/re-evaluation.

### G0.3.C4 — Source precedence

For each domain fact class define precedence.

Example: opportunity deadline

```text
current official solicitation revision
>
official Grants.gov/Simpler structured record
>
official agency page
>
trusted curated database
>
secondary web
>
user-provided value
```

Example: nonprofit tax-exempt status

```text
IRS official data
>
trusted nonprofit aggregator
>
organization website
>
client statement
```

When higher authority contradicts lower authority, lower value becomes superseded/conflicted rather than silently deleted.

### G0.3.C5 — Freshness semantics

Each source/fact class gets:

- expected refresh interval;
- soft-stale threshold;
- hard-stale threshold;
- on-demand refresh condition;
- deadline-near refresh behavior.

Example:

- open opportunity deadline/eligibility: aggressive refresh as deadline approaches;
- annual IRS filing data: slower refresh;
- ACS annual statistics: dataset-vintage based;
- organizational user preferences: event-driven rather than web freshness.

### G0.3.C6 — Evidence confidence

Confidence must not be a model's subjective scalar alone.

Components may include:

- source authority;
- directness;
- extraction quality;
- field normalization confidence;
- corroboration;
- recency/freshness;
- contradiction state;
- geography/population match for statistics.

Define states:

- VERIFIED;
- HIGH_CONFIDENCE;
- PROVISIONAL;
- CONFLICTED;
- STALE;
- REJECTED.

### G0.3.C7 — Conflict protocol

Possible outcomes:

- automatic precedence resolution;
- merge-compatible;
- unresolved conflict;
- human escalation;
- source refresh required;
- fact blocked from critical use.

Example:

If current official solicitation and old Grants.gov snapshot disagree on deadline, new official solicitation may supersede. If two equally authoritative records disagree, block critical use and escalate.

### G0.3.C8 — Data retention

Classes:

- canonical operational data;
- immutable source snapshots;
- generated artifacts;
- worker sidechains;
- audit records;
- temporary extraction/cache;
- PII-sensitive data.

Each gets retention, deletion, archive, encryption and legal policy placeholder.

### G0.3.C9 — Provenance chain

Minimum chain:

```text
SourceRegistry
  ↓
SourceSnapshot
  ↓
Extraction/Normalization Event
  ↓
EvidenceClaim / CanonicalFact / StatisticObservation
  ↓
EligibilityDecision / MatchExplanation / ResearchPack
  ↓
Application Section / Artifact
```

Every hop requires immutable IDs and version refs.

---

## 7.5 Initial Source Adapter Classes

P0/P1 design coverage:

### Federal opportunities

- Grants.gov;
- Simpler.Grants.gov;
- CommonGrants-compatible endpoints when available;
- SAM Assistance Listings.

### Federal awards/winners

- USAspending;
- SAM subawards where relevant;
- agency-specific systems such as TAGGS where useful.

### Organization verification

- IRS EO/BMF/990 data;
- Federal Audit Clearinghouse;
- ProPublica as secondary convenience layer.

### Community evidence

- Census ACS;
- SAIPE;
- BLS;
- BEA;
- CDC;
- USDA;
- NCES;
- HUD.

### State/private

- California centralized grant/open-data portal as initial state proof;
- registered private/foundation source via Crawl4AI;
- optional Candid later.

---

## 7.6 Implementation Work

Build a disposable source-protocol harness.

```text
prototype/g0/data/
  source_registry.py
  source_snapshot.py
  identifiers.py
  statistics.py
  source_change.py
  precedence.py
  freshness.py
  provenance.py
  fixtures/
```

Also create two test adapters:

1. a fixture-backed Grants.gov adapter;
2. a fixture-backed USAspending or Census adapter.

No live production service required yet. The objective is to prove the contracts can represent real source responses and revisions.

---

## 7.7 G0.3 Test Plan

### Snapshot tests

- same raw content → same hash but distinct retrieval event if policy requires;
- source snapshot is immutable;
- changed raw content → new snapshot;
- previous snapshot relationship preserved;
- parser version recorded;
- raw object unavailable → promotion blocked.

### Identifier tests

- valid EIN namespace/value format accepted;
- ALN normalization deterministic;
- duplicate external identifier merge behavior explicit;
- same identifier illegally assigned to incompatible entity → conflict;
- external ID absence does not prevent internal identity.

### Revision tests

Fixture:

```text
v1 deadline = Sep 15
v2 deadline = Sep 29
```

Expected:

- new SourceSnapshot;
- SourceChangeEvent materiality P0;
- prior deadline fact superseded;
- eligibility/application dependencies invalidated where relevant;
- CEO/project event queued for later runtime implementation.

### Precedence tests

- user-provided deadline vs current official solicitation → official wins;
- old official snapshot vs newer current official snapshot → newer effective version wins;
- two equal-authority conflicting values → CONFLICTED, no silent selection.

### Freshness tests

- stale source flagged;
- hard-stale critical fact blocked;
- deadline-near opportunity requires refresh;
- annual statistic does not become stale simply due to daily age if latest official vintage remains current.

### Statistic tests

- statistic lacking geography fails validation;
- statistic lacking reference period fails;
- percentage requires unit metadata;
- ACS estimate may preserve margin of error;
- using county statistic for city claim without transformation/qualification rejected.

### Provenance tests

Given an application sentence, system can trace:

```text
artifact section
→ evidence claim
→ statistic/fact
→ normalization event
→ source snapshot
→ source registry
```

Missing hop → FAIL.

### Conflict/adversarial tests

- malicious web page claims to override official grant instructions → cannot outrank source tier;
- source adapter mislabels issuer → schema/identity mismatch surfaced;
- stale cached page contradicts new API → current authoritative source wins;
- an LLM-generated statistic without source → cannot be promoted.

---

## 7.8 Deliverables

1. Data Constitution;
2. Source Registry contract;
3. Source Snapshot contract;
4. External Identifier namespace catalog;
5. Statistic Observation contract;
6. Source Change Event contract;
7. Source Precedence Matrix;
8. Freshness Policy Matrix;
9. Evidence Confidence Model;
10. Conflict Resolution Protocol;
11. Data Retention Policy;
12. Provenance Chain specification;
13. two real-source fixtures/adapters;
14. data-contract test suite;
15. Data Constitution Test Report.

---

## 7.9 Exit Gate

PASS only if:

- every promoted external fact can trace to a SourceSnapshot;
- every source has registered authority/freshness semantics;
- revisions create immutable new state;
- critical source conflicts cannot be silently resolved by an LLM;
- external identifiers are namespace-controlled;
- statistics require geography/time/methodology context;
- provenance chain is testable end-to-end.

---

# 8. Integrated G0.0–G0.3 Build Sequence

Recommended execution order:

```text
G0.0.C1 Evidence Inventory
        ↓
G0.0.C2 Decision Register
        ↓
G0.0.C3 Contradiction Sweep
        ↓
G0.0 Reality Lock
        ↓
G0.1.C1 Constitutional Laws
        ↓
G0.1.C2 Authority Ladder
        ↓
G0.1.C3 Capability Registry
        ↓
G0.1 policy stub + tests
        ↓
G0.2 Entity Boundaries
        ↓
G0.2 Identity + Relationships
        ↓
G0.2 CommonGrants Mapping
        ↓
G0.2 schema prototypes/tests
        ↓
G0.3 Source Registry
        ↓
G0.3 Snapshot/Identifiers/Statistics
        ↓
G0.3 precedence/freshness/revision/conflict
        ↓
G0.3 fixtures + provenance tests
        ↓
G0.0–G0.3 Reality Lock
```

Parallel work is allowed only where contracts do not depend on unresolved upstream decisions.

---

# 9. Master Testing Architecture

## 9.1 Test classes

### T1 — Document/contract completeness

Ensures required constitutional and schema artifacts exist.

### T2 — Schema validation

JSON/Pydantic/TypeSpec validation where applicable.

### T3 — Domain invariants

Tests entity relationships and prohibited states.

### T4 — Authority/security

Tests actor/capability/approval boundaries.

### T5 — Source/provenance

Tests source snapshots, lineage, revisions, precedence, freshness.

### T6 — Mapping/interoperability

Tests CommonGrants round trips and extension preservation.

### T7 — Adversarial

Contradictory docs, malformed external data, hostile web content, stale data, attempted agent authority escalation.

### T8 — Replay/reconstruction

Given archived snapshots and contracts, reconstruct the same material fact/decision state without relying on agent memory.

---

## 9.2 Reality Lock

A machine-readable G0.0–G0.3 lock should output:

```json
{
  "block": "G0.0-G0.3",
  "status": "PASS|FAIL",
  "p0_open": 0,
  "p1_open": 0,
  "required_artifacts_present": true,
  "authority_tests_pass": true,
  "domain_tests_pass": true,
  "common_grants_tests_pass": true,
  "source_provenance_tests_pass": true,
  "adversarial_tests_pass": true,
  "ready_for_g0_4": true
}
```

`ready_for_g0_4` must be computed from evidence, never hard-coded.

---

# 10. Evidence Package for Every Chapter

Every chapter completion must produce:

```text
PLAN
IMPLEMENTATION / CONTRACT ARTIFACTS
TEST FIXTURES
TEST RESULTS
OPEN ISSUES
DECISIONS / ADRS
KNOWN LIMITATIONS
NEXT-CHAPTER HANDOFF
```

No chapter is considered complete based on prose alone.

---

# 11. Development Agent Work Protocol

When Hermes/coding agents later execute this plan, each work packet should contain:

- exact chapter/section ID;
- objective;
- authoritative inputs;
- files allowed to change;
- files prohibited from changing;
- required outputs;
- test commands;
- exit criteria;
- escalation conditions;
- expected commit naming.

Example:

```yaml
work_packet_id: G0.2-C4-001
objective: implement and test CommonGrants Opportunity mapping
allowed_paths:
  - docs/grant-sector/g0/02-domain/
  - prototype/g0/domain/
prohibited_paths:
  - oce/
  - trading/
  - production repository
required_tests:
  - common_grants_opportunity_roundtrip
  - extension_preservation
exit_gate:
  - zero failing P0 mapping tests
```

This prevents agents from turning constitutional work into uncontrolled refactoring.

---

# 12. Commit / Versioning Strategy

Recommended commit checkpoints:

```text
G0.0-C1 evidence manifest
G0.0-C2 decision register
G0.0-C3 contradiction closure
G0.0-R ratification lock

G0.1-C1 constitution
G0.1-C2 authority ladder
G0.1-C3 capability registry
G0.1-R authority tests

G0.2-C1 ontology
G0.2-C2 identity/relations
G0.2-C3 schema contracts
G0.2-C4 CommonGrants mapping
G0.2-R domain lock

G0.3-C1 source registry
G0.3-C2 snapshot/identifier/statistic contracts
G0.3-C3 precedence/freshness/change/conflict
G0.3-C4 provenance fixtures/tests
G0.3-R data lock

G0.0-03-R FINAL REALITY LOCK
```

Do not squash away the ratification lineage while G0 is active.

---

# 13. Acceptance Metrics

G0.0–G0.3 is primarily correctness-oriented rather than throughput-oriented.

Target metrics:

- unresolved P0 architecture contradictions: **0**;
- consequential capability classes with explicit policy: **100%**;
- core entities with identity rules: **100%**;
- CommonGrants mapped fields classified: **100%**;
- promoted fact types requiring source lineage: **100%**;
- critical source precedence classes covered: **100%**;
- source revision test cases correctly invalidating downstream state: **100%**;
- adversarial authority escalation blocked: **100%**;
- provenance chain completeness in fixtures: **100%**;
- secret-in-memory allowed paths: **0**.

---

# 14. Definition of Done for G0.0–G0.3

The block is DONE only when:

1. all required deliverables exist;
2. ratification artifacts are versioned;
3. authority model is executable/tested;
4. ontology/schema prototypes pass;
5. CommonGrants mapping passes fixtures;
6. data constitution handles real source fixtures;
7. source amendment replay passes;
8. all P0 contradictions are closed;
9. final Reality Lock outputs PASS;
10. the G0.4 team can implement Dual-Hermes protocol/memory without redefining product/domain/data authority.

---

# 15. Immediate Execution Order

Start with **G0.0.C1–C3**.

The first execution session should:

1. build the R0 artifact manifest;
2. normalize every major R0 decision;
3. run contradiction analysis;
4. produce the unresolved decision ledger;
5. resolve all P0 contradictions;
6. freeze non-goals and bake-off candidates;
7. run the first R0 Ratification Reality Lock.

Only after that PASS should implementation proceed into **G0.1 Product Constitution & Authority**.

---

# 16. Block-Level Handoff to G0.4

When G0.0–G0.3 closes, G0.4 receives:

- ratified architectural laws;
- actor/capability matrix;
- stable entity schemas;
- CommonGrants compatibility map;
- Source Registry;
- Source Snapshot;
- External Identifier catalog;
- Statistic Observation;
- source precedence/freshness/revision rules;
- provenance requirements;
- immutable IDs and audit expectations.

G0.4 may then safely define `IntentContract`, `TaskContract`, worker packets, sidechains, and memory promotion rules without inventing upstream truth semantics.
