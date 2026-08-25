# G0 Book 3 — Grant Intelligence Data Constitution Master Implementation Plan

**Document ID:** GS-G0-B3-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR CONTINUOUS EXECUTION AFTER BOOK 2 RATIFICATION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Parent plan:** `G0_FULL_MASTER_BUILD_BLUEPRINT_v1.0.md`  
**Receives from:** Book 0 R0 Ratification + Book 1 Product Constitution & Authority + Book 2 Grant Domain Ontology  
**Hands off to:** Book 4 Dual-Hermes Protocol & Memory Constitution  
**Unlocks:** D0 Shadow Draft Harness after ratification

---

# 0. Book Mission

Book 3 defines how **outside reality is allowed to enter the product**.

Book 1 established who may act and under what authority. Book 2 established what the core grant-domain objects mean. Book 3 now establishes the rules by which real external information becomes source material, evidence, canonical facts, statistics, revisions, requirements, award history and ultimately usable application context.

This is the book where the architecture stops being a clean internal model and collides with the actual world:

- government APIs change;
- web pages are amended without warning;
- PDFs disagree with portal metadata;
- deadlines move;
- grant amounts change;
- organization names differ across IRS/SAM/state systems;
- state sites have weak identifiers;
- private funders may expose only webpages;
- award databases may omit the original opportunity;
- Census statistics have geography, vintage and margin-of-error semantics;
- crawled pages can contain hostile instructions;
- old cached data can look authoritative;
- client statements can conflict with official records;
- extraction pipelines can corrupt tables or dates;
- source systems can go temporarily offline;
- data may be correct but too stale to use for a live grant decision.

The mission of Book 3 is therefore:

> Build a source, provenance, freshness, revision and conflict constitution strong enough that every operational fact can answer **where did this come from, when was it true, what version was used, what authority does it have, what conflicts with it, and what downstream work depends on it?**

When Book 3 is complete, the D0 Shadow Draft Harness can produce the first grounded Georgia-first mock proposal using a manually approved profile plus registered/snapshotted real opportunity/evidence fixtures without depending on hidden agent memory or uncontrolled web research.

---

# 1. Book Theme

## Register → Capture → Normalize → Evaluate → Promote → Monitor → Revise → Replay

```text
BOOK 2 DOMAIN SEMANTICS
        ↓
SOURCE REGISTRY
        ↓
IMMUTABLE SNAPSHOT
        ↓
PARSER / EXTRACTION EVENT
        ↓
NORMALIZATION
        ↓
CLAIM / STATISTIC / IDENTIFIER CANDIDATE
        ↓
AUTHORITY + FRESHNESS + CONFIDENCE
        ↓
PROMOTION / CONFLICT
        ↓
CANONICAL OPERATIONAL USE
        ↓
CHANGE DETECTION
        ↓
DEPENDENCY INVALIDATION
        ↓
REPLAY / AUDIT
```

The product should be able to forget an agent session and still reconstruct the same material decision from stored source state and deterministic transformation records.

---

# 2. Hard Inputs from Books 1–2

Book 3 may not redefine these without explicit amendment:

1. agent memory is not canonical truth;
2. external facts require provenance;
3. external provider IDs never replace internal identity;
4. `EvidenceClaim` and `CanonicalFact` are distinct;
5. `SourceSnapshot` and `Artifact` are distinct;
6. `StatisticObservation` preserves geography/population/time/methodology semantics;
7. `GrantOpportunity` has stable identity while material terms live in `OpportunityRevision`;
8. eligibility decisions target exact opportunity revisions and exact supporting facts;
9. `ApplicationProject` targets exact opportunity revision;
10. material opportunity changes invalidate dependent decisions;
11. facts/claims can conflict without silent overwrite;
12. deterministic constraints remain deterministic after normalization;
13. tenant scope is mandatory;
14. safe drafting is L2; submission remains disabled;
15. proposal and business plan remain separate artifacts;
16. CommonGrants is an interoperability surface, not internal sovereignty;
17. Georgia is first state proof priority while the architecture remains jurisdiction-agnostic;
18. D0 DraftContextBundle must be reconstructable without agent memory.

Book 3 may extend source-specific metadata but must not reshape domain objects merely because an upstream API is inconvenient.

---

# 3. Design Philosophy

## 3.1 Raw source state is evidence, not an implementation nuisance

Whenever external information materially influences eligibility, matching, grant writing or advice, the product must preserve enough raw source state to reconstruct what the system actually saw.

## 3.2 Immutable capture before interpretation

Capture first, parse second.

A parser or LLM should never be the only record of what an external source contained.

## 3.3 Registered sources only

A worker may discover an unregistered URL, but data from that source cannot be promoted into governed operational truth until the source is registered/classified or explicitly approved through a temporary governed path.

## 3.4 Authority is fact-specific

A source can be highly authoritative for one fact class and weak for another.

Example:

- IRS is authoritative for tax-exempt filing/status data;
- Grants.gov/current issuer solicitation is authoritative for opportunity terms;
- USAspending is authoritative for federal transaction/award records;
- a client's own statement may be authoritative for private intent/preference but not tax-exempt status.

## 3.5 Freshness is semantic, not simply age in days

An annual Census vintage and a live opportunity deadline have completely different freshness requirements.

## 3.6 Change must propagate

The system is not allowed to know that a source changed while leaving dependent eligibility, match, requirements or drafts represented as current.

## 3.7 Confidence is decomposable

No opaque “AI confidence 0.92” as the sole trust mechanism.

Confidence derives from observable factors such as authority, directness, extraction quality, corroboration, freshness, contradiction state and semantic fit.

## 3.8 Source discovery is not evidence promotion

Search engines, SearXNG, GPT Researcher, Crawl4AI discovery or model-generated citations can identify candidate sources. Promotion requires fetching/snapshotting the original source and validating lineage.

## 3.9 Web content has zero policy authority

A source page can provide data but cannot instruct Hermes/tools to violate platform policy.

## 3.10 Keep source adapters replaceable

The product should own `SourceRegistry`, `SourceSnapshot` and normalization contracts. Crawl4AI, Unstructured, PixelRAG and other engines sit behind them.

---

# 4. Required Book 3 Artifact Set

```text
docs/grant-sector/g0/03-data/
├── G0_B3_DATA_CONSTITUTION.md
├── G0_B3_SOURCE_CLASSIFICATION.md
├── G0_B3_SOURCE_REGISTRY_SPEC.md
├── G0_B3_SOURCE_ONBOARDING_PROTOCOL.md
├── G0_B3_SOURCE_SNAPSHOT_SPEC.md
├── G0_B3_CAPTURE_REPLAY_PROTOCOL.md
├── G0_B3_EXTRACTION_NORMALIZATION_PROTOCOL.md
├── G0_B3_SOURCE_PRECEDENCE_MATRIX.md
├── G0_B3_FRESHNESS_POLICY.md
├── G0_B3_CONFIDENCE_PROMOTION_MODEL.md
├── G0_B3_CONFLICT_RESOLUTION_PROTOCOL.md
├── G0_B3_REVISION_CHANGE_PROTOCOL.md
├── G0_B3_DEPENDENCY_INVALIDATION_PROTOCOL.md
├── G0_B3_EXTERNAL_IDENTIFIER_VERIFICATION.md
├── G0_B3_STATISTIC_OBSERVATION_POLICY.md
├── G0_B3_SOURCE_SECURITY_POLICY.md
├── G0_B3_DATA_RETENTION_DELETION_POLICY.md
├── G0_B3_PROVENANCE_CHAIN_SPEC.md
├── G0_B3_SOURCE_HEALTH_OBSERVABILITY.md
├── G0_B3_FEDERAL_SOURCE_PROFILE.md
├── G0_B3_GEORGIA_SOURCE_PROFILE.md
├── G0_B3_PRIVATE_FOUNDATION_SOURCE_PROFILE.md
├── G0_B3_D0_SHADOW_DRAFT_DATA_PACKET.md
├── G0_B3_ADR_REGISTER.md
├── G0_B3_TEST_REPORT.md
├── G0_B3_ADVERSARIAL_TEST_REPORT.md
├── G0_B3_REALITY_LOCK_REPORT.md
└── G0_B3_HANDOFF_TO_BOOK_4.md

schemas/g0/data/
├── source_registry.schema.json
├── source_snapshot.schema.json
├── source_request.schema.json
├── capture_event.schema.json
├── extraction_event.schema.json
├── normalization_event.schema.json
├── source_change_event.schema.json
├── fact_promotion.schema.json
├── source_conflict.schema.json
├── freshness_state.schema.json
├── source_health.schema.json
├── provenance_edge.schema.json
└── data_retention_class.schema.json

config/g0/data/
├── source_classes.yaml
├── authority_tiers.yaml
├── source_registry_seed.yaml
├── precedence_matrix.yaml
├── freshness_matrix.yaml
├── materiality_rules.yaml
├── promotion_thresholds.yaml
├── source_health_policies.yaml
└── retention_classes.yaml

prototype/g0/data/
├── source_registry.py
├── snapshot.py
├── hash_identity.py
├── precedence.py
├── freshness.py
├── confidence.py
├── conflicts.py
├── change_detection.py
├── invalidation.py
├── provenance.py
├── replay.py
└── fixtures/

tests/g0/book3/
├── test_source_registry.py
├── test_source_onboarding.py
├── test_snapshot_immutability.py
├── test_capture_replay.py
├── test_extraction_normalization.py
├── test_precedence.py
├── test_freshness.py
├── test_confidence_promotion.py
├── test_conflicts.py
├── test_change_materiality.py
├── test_dependency_invalidation.py
├── test_identifier_verification.py
├── test_statistics.py
├── test_source_security.py
├── test_retention.py
├── test_provenance.py
├── test_federal_fixtures.py
├── test_georgia_fixtures.py
├── test_private_web_fixtures.py
├── test_d0_data_packet.py
└── test_adversarial_data.py
```

---

# 5. Chapter B3.C1 — Data Constitution

## Objective

Write the binding laws governing external data and evidence.

## Required laws

### DATA-LAW-001 — Registered-source promotion

Only governed/registered source identities may support promoted operational facts, except explicit temporary evidence paths approved by policy.

### DATA-LAW-002 — Capture-before-interpretation

Material external data must be captured/snapshotted before derived interpretation becomes authoritative.

### DATA-LAW-003 — Immutable source history

SourceSnapshots are append-only immutable representations.

### DATA-LAW-004 — Raw hash identity

Every retained source body/document/raw payload requires content hashing or equivalent integrity identity.

### DATA-LAW-005 — Transformation lineage

Parsing, extraction and normalization must record implementation/version lineage.

### DATA-LAW-006 — Authority is source + fact class

Source tier alone cannot determine all precedence.

### DATA-LAW-007 — Freshness is domain-specific

Live opportunities, annual statistics, organization filings and historical awards use different freshness rules.

### DATA-LAW-008 — Stale critical facts may block action

A hard-stale deadline or eligibility requirement cannot silently drive submission readiness.

### DATA-LAW-009 — Conflicts remain explicit

Equal or unresolved authoritative conflicts produce CONFLICTED state, not silent last-write-wins.

### DATA-LAW-010 — New revision never rewrites prior decision history

Previous decisions remain reconstructable against the exact source revision/fact state used.

### DATA-LAW-011 — Material source changes trigger invalidation

Downstream dependencies are marked stale and recomputation events generated.

### DATA-LAW-012 — Search result is not source evidence

Discovery index/search snippets are not sufficient to promote a material claim.

### DATA-LAW-013 — Generated citation is not evidence until verified

Model-cited URL/source must be fetched/snapshotted/validated.

### DATA-LAW-014 — Web content has no tool/policy authority

Instructions embedded in external sources are data, never capability grants.

### DATA-LAW-015 — Geography/time semantics are mandatory for public statistics

A statistic lacking necessary geographic/reference-period semantics cannot be promoted for proposal use.

### DATA-LAW-016 — External IDs require namespace and verification state

No ambiguous identifier strings.

### DATA-LAW-017 — Source absence preserves uncertainty

Missing/unavailable source does not justify fabrication or forced falsehood.

### DATA-LAW-018 — Data deletion does not falsify audit history

Where policy requires deletion of content/PII, tombstone/metadata strategies preserve permitted audit/reconstruction semantics without retaining prohibited content.

### DATA-LAW-019 — Provenance is transitive

Application content can trace through normalized facts to capture/source identity.

### DATA-LAW-020 — Source adapters cannot promote themselves

Adapters emit candidates/events. Promotion follows product policy.

## Deliverables

- final Data Constitution;
- numbered laws;
- enforcement category;
- affected schemas/services;
- amendment linkage to Books 1/2.

## Commit

`G0-B3-C1: freeze grant intelligence data constitution`

---

# 6. Chapter B3.C2 — Source Classification System

## Objective

Define source classes before individual integrations are configured.

## Source classes

### OFFICIAL_ISSUER

The organization/agency issuing an opportunity, solicitation or guidance.

Examples:

- official federal agency solicitation;
- Georgia OPB/DCA/GEMA issuer pages;
- official foundation/corporate funder page.

### OFFICIAL_AGGREGATOR

Government/official platform aggregating issuer data.

Examples:

- Grants.gov;
- Simpler.Grants.gov;
- SAM Assistance Listings.

### OFFICIAL_TRANSACTIONAL

Official award/transaction record.

Examples:

- USAspending;
- SAM subaward datasets;
- FAC;
- agency award databases.

### OFFICIAL_STATISTICAL

Government/statistical authority.

Examples:

- Census ACS/SAIPE;
- BLS;
- BEA;
- CDC;
- USDA;
- NCES;
- HUD.

### TRUSTED_CURATED

High-quality institutional secondary/aggregated source.

Examples:

- ProPublica nonprofit explorer;
- Candid if licensed;
- trusted nonprofit/funder datasets.

### GOVERNED_WEB

Registered funder/organization/research webpage captured by crawler.

### USER_PROVIDED

Client uploads/statements/manual data.

### DERIVED_INTERNAL

Product-derived structured data whose parent evidence remains external/user-provided.

## Authority tiers

Recommended general tiers:

- A — primary official issuer/authority;
- B — official transactional/statistical record;
- C — trusted curated institutional secondary;
- D — governed web secondary;
- E — user-provided/unverified.

But actual precedence is fact-class-specific.

## Tests

- every registered source has class and authority tier;
- derived internal objects cannot pretend to be external authority;
- source class alone does not bypass fact-specific precedence.

---

# 7. Chapter B3.C3 — SourceRegistry Contract

## Objective

Create the canonical registry of allowed source integrations.

## Required fields

```yaml
source_id:
name:
description:
source_class:
authority_tier:
owner_organization:
jurisdiction:
domain_categories:
access_modes:
base_urls:
api_base_url:
auth_mode:
credential_scope_ref:
expected_update_frequency:
default_freshness_policy:
terms_policy_ref:
robots_policy_ref:
rate_limit_policy_ref:
adapter_name:
adapter_version:
parser_strategy:
health_policy_ref:
pii_classification:
retention_class:
enabled:
created_at:
updated_at:
```

## Source identity rule

`source_id` identifies a governed logical source, not one fetched page.

Examples:

```text
src_grants_gov
src_simpler_grants
src_usaspending
src_irs_eo
src_census_acs
src_ga_opb_grants
src_ga_dca
src_foundation_xyz
```

## Domain categories

A source may cover one or more:

- opportunities;
- programs;
- awards;
- organizations;
- statistics;
- funders;
- requirements;
- application instructions;
- outcomes.

## Deliverables

- SourceRegistry schema;
- seed registry covering initial federal/Georgia/statistical sources;
- validation rules.

## Tests

- duplicate source ID rejected;
- source without authority classification rejected;
- enabled web source without terms/robots review state rejected or explicitly marked pending;
- auth-required source missing credential scope rejected;
- adapter version required for enabled machine source.

## Commit

`G0-B3-C2-C3: define source classes and canonical SourceRegistry`

---

# 8. Chapter B3.C4 — Source Onboarding & Governance Protocol

## Objective

Ensure adding a source is controlled and repeatable.

## Lifecycle

```text
CANDIDATE
  ↓
IDENTITY / OWNERSHIP CHECK
  ↓
TERMS / ROBOTS / ACCESS REVIEW
  ↓
AUTHORITY CLASSIFICATION
  ↓
DATA-SHAPE ANALYSIS
  ↓
ADAPTER / CAPTURE STRATEGY
  ↓
FIXTURE CAPTURE
  ↓
SCHEMA / PARSER TESTS
  ↓
RATE-LIMIT + FAILURE TEST
  ↓
SECURITY / PROMPT-INJECTION TEST
  ↓
SOURCE HEALTH POLICY
  ↓
ENABLED
```

## Source statuses

- CANDIDATE;
- REVIEWING;
- FIXTURE_ONLY;
- ENABLED;
- DEGRADED;
- DISABLED;
- RETIRED.

## Source onboarding packet

```text
Source identity
Legal/access notes
Authority/fact classes
Example resources
Expected IDs
Capture approach
Parser approach
Freshness rule
Failure behavior
Health probes
Test fixture refs
Security notes
Operational owner
```

## Hard rule

An agent discovering a useful site may create a `SourceCandidate` or research note. It may not automatically add that domain to production allowlists.

## Tests

- unreviewed source cannot be enabled;
- disabled source cannot promote new data;
- source version changes require adapter/test update where material.

---

# 9. Chapter B3.C5 — SourceSnapshot Contract

## Objective

Define the immutable unit of captured outside state.

## Required fields

```yaml
snapshot_id:
source_id:
tenant_id: null|...
resource_type:
external_resource_id:
canonical_url:
request_id:
request_fingerprint:
retrieved_at:
source_effective_at:
source_published_at:
http_status:
http_headers_subset:
content_type:
content_length:
raw_object_uri:
raw_hash:
raw_hash_algorithm:
adapter_name:
adapter_version:
capture_method:
previous_snapshot_id:
revision_key:
source_etag:
source_last_modified:
snapshot_status:
```

## Capture methods

- API_JSON;
- API_XML;
- BULK_FILE;
- HTML;
- PDF;
- DOCX;
- IMAGE;
- MANUAL_UPLOAD;
- USER_FORM;
- OTHER governed extension.

## Snapshot status

- CAPTURED;
- VERIFIED_INTEGRITY;
- PARTIAL;
- FAILED_CAPTURE;
- REDACTED;
- TOMBSTONED.

## Immutable rule

No update-in-place to raw body/hash/meaningful capture metadata.

Corrections create a new capture/snapshot or metadata correction event with lineage.

## Same content / new retrieval

Architecture must decide whether identical raw content on a later retrieval creates:

- a new RetrievalEvent pointing to the same content-addressed object; or
- a new SourceSnapshot with same hash.

Recommended: separate `CaptureEvent`/retrieval occurrence from deduplicated raw object storage so timing can be preserved without duplicating bytes.

## Tests

- mutation attempt rejected;
- raw hash deterministic;
- identical content deduplicates bytes but preserves retrieval events;
- changed content creates new snapshot lineage;
- missing raw object blocks promotion for material facts.

## Commit

`G0-B3-C4-C5: freeze source onboarding and immutable snapshot semantics`

---

# 10. Chapter B3.C6 — Capture, Replay & Content-Addressed Storage Protocol

## Objective

Make external data reproducible and economically storeable.

## Capture pipeline

```text
SourceRequest
   ↓
HTTP/API/Browser Fetch
   ↓
CaptureEvent
   ↓
Raw Blob Hash
   ↓
Object Store
   ↓
SourceSnapshot Metadata
```

## Replay requirement

Given:

- SourceSnapshot;
- raw object;
- adapter/parser version or archived transformation container/package identity;

we should be able to reproduce normalized extraction or explicitly report why historical implementation is unavailable.

## Raw object storage

Must support:

- content-addressing;
- encryption at rest;
- tenant/security metadata;
- integrity validation;
- lifecycle/retention classes;
- immutable references.

Technology choice deferred to G1/Book 9; contract freezes now.

## Replay classes

- EXACT_REPLAY — same code/version available;
- COMPATIBLE_REPLAY — newer compatible parser against raw capture;
- PARTIAL_REPLAY — raw source exists but exact transformation unavailable;
- NON_REPLAYABLE — unacceptable for promoted critical data unless explicitly exempted.

## Tests

- capture→replay fixture equality;
- corrupt blob fails hash verification;
- parser upgrade can reprocess old raw capture without refetching;
- source disappears from web but historical snapshot remains replayable under retention policy.

---

# 11. Chapter B3.C7 — Extraction & Normalization Event Model

## Objective

Separate what the source contained from what our software inferred/normalized.

## ExtractionEvent

```yaml
extraction_event_id:
snapshot_id:
engine:
engine_version:
strategy:
started_at:
completed_at:
quality_metrics:
output_artifact_ref:
status:
errors:
```

Engines may include:

- deterministic JSON mapper;
- HTML parser;
- Unstructured;
- MarkItDown;
- OpenDataLoader PDF;
- OCR/Chandra;
- PixelRAG fallback;
- LLM structured extraction.

## NormalizationEvent

```yaml
normalization_event_id:
extraction_event_id:
normalizer_name:
normalizer_version:
target_schema:
source_fields:
output_entity_or_claim_refs:
confidence_components:
validation_status:
```

## Rule

LLM extraction output is a candidate structured representation, not an automatic CanonicalFact.

## Parser quality signals

Possible:

- text completeness;
- table retention;
- OCR confidence;
- field coverage;
- schema validity;
- citation/localization support;
- page/section mapping.

## Tests

- same raw snapshot supports multiple extraction strategies without overwriting prior outputs;
- parser version lineage preserved;
- invalid schema extraction fails normalization;
- low extraction confidence cannot silently become VERIFIED fact.

## Commit

`G0-B3-C6-C7: define capture replay and extraction normalization lineage`

---

# 12. Chapter B3.C8 — Source Precedence Matrix

## Objective

Determine which source should govern which fact class when sources disagree.

## Fact classes

At minimum:

- opportunity title;
- opportunity status;
- deadline;
- award ceiling/floor;
- estimated funding;
- eligibility;
- matching/cost share;
- required attachments;
- application questions;
- submission instructions;
- funder identity;
- program/ALN;
- historical award amount;
- recipient identity;
- tax-exempt status;
- legal organization name;
- organization financial filing facts;
- community statistics;
- user preferences/intention;
- internal project goals.

## Example precedence — opportunity deadline

```text
current official solicitation / official issuer amendment
>
current Grants.gov/Simpler official record
>
official agency landing page
>
trusted curated database
>
registered secondary web
>
user recollection/manual entry
```

## Example — nonprofit tax-exempt status

```text
current IRS official record
>
trusted nonprofit aggregator derived from IRS
>
organization website
>
client statement
```

## Example — client program intent

```text
current client-approved canonical project facts
>
old client conversation summary
>
third-party description
```

## Example — historical federal award transaction

```text
official transactional award record / agency source
>
trusted curated grant database
>
funder press release
>
recipient website
```

## Equal-authority conflict

No automatic last-write-wins.

Status becomes CONFLICTED/REVIEW_REQUIRED unless a temporal/effective-date rule resolves it.

## Tests

- fact-specific precedence works;
- higher generic source tier does not incorrectly outrank specialized authoritative source;
- client intent facts can outrank government data only for facts the client controls, not legal/issuer facts.

---

# 13. Chapter B3.C9 — Freshness Constitution

## Objective

Define when data is current enough for its intended use.

## Freshness states

- FRESH;
- SOFT_STALE;
- HARD_STALE;
- UNKNOWN_FRESHNESS;
- HISTORICAL_FIXED.

## Policy fields

```yaml
fact_class:
source_class:
soft_stale_after:
hard_stale_after:
refresh_on_access:
refresh_on_deadline_window:
latest_vintage_rule:
critical_use_block_on_hard_stale:
```

## Example policies

### Active opportunity deadline/eligibility

High refresh sensitivity. Near-deadline applications may require forced refresh before readiness.

### Historical award

Historical-fixed once verified, except correction/revision discovery.

### IRS annual filing facts

Vintage-based; not stale merely because more than N days old if latest official available filing remains that vintage.

### ACS/SAIPE

Dataset-vintage based. Must distinguish reference period from retrieval time.

### Web funder priorities

Moderate refresh; refresh before material application drafting if source is time-sensitive.

## Deadline proximity tiers

Suggested later configurable policy:

- >30 days;
- 14–30 days;
- 7–14 days;
- <7 days;
- <24 hours.

Closer deadline → stronger refresh/health requirements.

## Tests

- same age produces different freshness for different fact classes;
- annual statistic latest-vintage remains valid;
- hard-stale deadline blocks submission-ready state;
- historical fixed award remains valid absent correction.

## Commit

`G0-B3-C8-C9: freeze source precedence and freshness semantics`

---

# 14. Chapter B3.C10 — Evidence Confidence & Promotion Model

## Objective

Define how candidate claims become usable evidence/canonical facts.

## Confidence components

Recommended normalized components:

- source authority;
- directness of support;
- extraction quality;
- normalization confidence;
- corroboration;
- freshness;
- contradiction state;
- identity resolution confidence;
- geography/population fit;
- temporal applicability.

## Promotion states

- CANDIDATE;
- PROVISIONAL;
- VERIFIED;
- CONFLICTED;
- STALE;
- REJECTED;
- SUPERSEDED.

## Promotion policy

Critical fact classes require stronger rules than narrative/contextual research.

Examples:

### Deadline / eligibility / amount

Require official/direct source or explicit governed exception.

### Community context statement

May permit multiple credible institutional sources with appropriate citation and caveats.

### Client-internal business goal

Client approval may be the controlling authority.

## No opaque scalar requirement

A total score may be computed for ranking, but underlying components and decision reason must remain available.

## Promotion event

```yaml
promotion_event_id:
claim_id:
target_fact_id:
old_state:
new_state:
reason_codes:
policy_version:
source_refs:
approval_ref:
created_at:
```

## Tests

- LLM self-confidence alone cannot verify;
- official direct fresh source can satisfy critical promotion policy;
- contradicted claim cannot remain VERIFIED without resolution;
- user-approved internal goal can promote under appropriate fact class.

---

# 15. Chapter B3.C11 — Conflict Resolution Protocol

## Objective

Resolve disagreement without destroying evidence lineage.

## Conflict object

```yaml
conflict_id:
subject_entity_id:
fact_class:
claim_refs:
source_refs:
conflict_type:
severity:
resolution_status:
resolution_method:
resolved_value_ref:
resolver_actor:
resolved_at:
```

## Conflict types

- VALUE_CONFLICT;
- TEMPORAL_CONFLICT;
- IDENTITY_CONFLICT;
- GEOGRAPHY_CONFLICT;
- UNIT_CONFLICT;
- SOURCE_VERSION_CONFLICT;
- INTERPRETATION_CONFLICT;
- USER_OFFICIAL_CONFLICT.

## Resolution methods

- SOURCE_PRECEDENCE;
- EFFECTIVE_DATE;
- SOURCE_REFRESH;
- MERGE_COMPATIBLE;
- HUMAN_REVIEW;
- OFFICIAL_CLARIFICATION;
- UNRESOLVED_BLOCK.

## Critical-use block

If unresolved conflict affects:

- deadline;
- eligibility;
- amount;
- required attachments;
- legal identity;
- submission method;

then readiness status must block or clearly degrade.

## Tests

- lower-authority stale value becomes superseded, not deleted;
- equal-authority contradiction blocks critical use;
- human resolution references evidence and actor.

---

# 16. Chapter B3.C12 — Revision & Source Change Protocol

## Objective

Convert changing source state into explicit governed events.

## SourceChangeEvent

```yaml
change_event_id:
source_id:
entity_type:
entity_id:
old_snapshot_id:
new_snapshot_id:
detected_at:
change_class:
materiality:
affected_fields:
semantic_diff_ref:
status:
```

## Materiality classes

### P0 — application-critical

- eligibility changed;
- deadline changed;
- award ceiling/floor or match requirement changed materially;
- required attachment/form changed;
- submission path changed;
- geography changed;
- opportunity cancelled;
- mandatory application question/rubric changed.

### P1 — significant strategy/research

- program description/priorities changed;
- scoring guidance changed;
- contact changed;
- explanatory guidance changed;
- historical award data corrected.

### P2 — nonmaterial

- formatting;
- navigation;
- nonsemantic typo;
- irrelevant site chrome.

## Semantic diff

Raw byte diff is not enough. The system must eventually support structured field/requirement diff.

## Tests

- deadline amendment classified P0;
- formatting change classified P2;
- parser output change with unchanged raw source distinguished from true source change.

## Commit

`G0-B3-C10-C12: define promotion, conflict and source-change governance`

---

# 17. Chapter B3.C13 — Dependency Invalidation Protocol

## Objective

Ensure stale upstream facts cannot masquerade as current downstream work.

## Dependency types

- EligibilityDecision depends on OpportunityRevision + organization/project facts;
- MatchExplanation depends on opportunity/facts/research/weights;
- Requirement set depends on OpportunityRevision;
- DraftContextBundle depends on revision/requirements/evidence;
- proposal section depends on requirements/facts/evidence/statistics;
- budget depends on amount limits/match rules/project assumptions;
- SubmissionPackage depends on approved artifact versions and current requirements.

## Invalidation states

- CURRENT;
- STALE_RECOMPUTE_REQUIRED;
- STALE_REVIEW_REQUIRED;
- INVALID;
- SUPERSEDED.

## Event propagation example

```text
Deadline / eligibility amendment
        ↓
new SourceSnapshot
        ↓
SourceChangeEvent P0
        ↓
new OpportunityRevision
        ↓
EligibilityDecision = STALE
Match = STALE
Requirements = STALE
DraftContext = STALE
ApplicationProject = REVIEW_REQUIRED
        ↓
recompute/review work queued later at runtime
```

## Selective invalidation

Do not regenerate the entire world for every source update.

Track dependency edges so only affected decisions/artifacts require recompute.

## Tests

- deadline-only change does not necessarily invalidate unrelated historical winner research;
- eligibility change invalidates eligibility and readiness;
- budget ceiling change invalidates budget/financial consistency;
- nonmaterial P2 change does not invalidate application.

---

# 18. Chapter B3.C14 — External Identifier Verification Protocol

## Objective

Operationalize the Book 2 identifier model against external sources.

## Verification states

- UNVERIFIED;
- USER_ASSERTED;
- SOURCE_ASSERTED;
- VERIFIED_OFFICIAL;
- CONFLICTED;
- EXPIRED/SUPERSEDED.

## Verification event

Records:

- identifier namespace;
- value;
- entity;
- verifying source snapshot;
- method;
- effective period;
- result.

## Examples

### EIN

Client provides EIN → USER_ASSERTED.

IRS record matches → VERIFIED_OFFICIAL.

### UEI

SAM source supports → VERIFIED_OFFICIAL.

### FIPS

Geography resolver validates → VERIFIED_OFFICIAL/REFERENCE.

### Georgia portal ID

Issuer portal snapshot verifies provider-specific identifier.

## Tests

- external ID claimed in chat does not become verified automatically;
- conflicting verified IDs trigger identity conflict;
- same value in different namespaces remains distinct.

## Commit

`G0-B3-C13-C14: define dependency invalidation and identifier verification`

---

# 19. Chapter B3.C15 — StatisticObservation Data Policy

## Objective

Make quantitative community/impact evidence safe for grant writing.

## Required dimensions

```text
metric_code
metric_label
value
unit
geography_type
geography_id / FIPS where applicable
geography_label
population_scope
reference_period_start/end
dataset_name
dataset_vintage/version
estimate_type
margin_of_error
confidence_interval
methodology_ref
source_snapshot_ref
quality_state
```

## Geography rules

A statistic should not silently cross geography levels.

Examples:

- Fulton County statistic cannot be described as City of Atlanta statistic;
- Georgia statewide statistic cannot be represented as local-county fact;
- census tract estimates require explicit tract identity.

## Population rules

Preserve denominator/population semantics.

Examples:

- all persons;
- children under 18;
- single-parent households;
- labor force participants;
- school-age population.

## Time rules

Distinguish:

- reference period;
- dataset release/vintage;
- retrieval time.

## Derived statistics

If the platform computes a derived rate/aggregation, record transformation lineage, formula and parent observations.

## Proposal-use rule

Client-facing narrative must not overstate precision beyond source methodology. Margin-of-error/estimate caveats should be available to QA/generation.

## Tests

- geography mismatch flagged;
- missing reference period rejected;
- percentage without denominator context where required flagged;
- derived statistic replays from parents;
- stale vintage policy applied correctly.

---

# 20. Chapter B3.C16 — Federal Source Profiles

## Objective

Define the first authoritative federal data lanes in enough detail for fixture-backed tests and G1 implementation.

## Initial federal profiles

### Grants.gov / Simpler.Grants.gov

Role:

- active/historical opportunities;
- opportunity metadata;
- eligibility/application information;
- revision data where exposed.

Priority facts:

- opportunity number;
- title;
- agency;
- status;
- open/close dates;
- award ranges;
- eligibility/applicant types;
- ALN/program links;
- attachments/instructions.

### SAM Assistance Listings

Role:

- durable federal program/assistance-listing context.

### USAspending

Role:

- federal awards/transactions;
- recipient/winner history;
- amounts/geography/program IDs where available.

### SAM Subaward / agency-specific award systems

Optional enrichment where relevant.

### IRS EO/BMF/990

Role:

- nonprofit legal/status/filing information.

### Federal Audit Clearinghouse

Role:

- federal award/audit capacity history where applicable.

### Census ACS / SAIPE

Role:

- demographic/economic/community need statistics.

### BLS / BEA / CDC / USDA / NCES / HUD

Role:

- domain-specific impact/context statistics when appropriate.

## Source profile template

Each profile records:

```text
SourceRegistry seed
fact classes
identifier namespaces
capture method
expected revision semantics
freshness policy
rate-limit/auth notes
fixture examples
known caveats
fallbacks
```

## Tests

At least one real captured/archived fixture for opportunity, award, organization verification and statistic classes validates against schemas.

---

# 21. Chapter B3.C17 — Georgia Source Profiles

## Objective

Make Georgia the first state-level source fabric proof.

## Initial targets

### Georgia Governor’s Office of Planning and Budget / Georgia Grants Portal

Use for:

- current state opportunities/programs;
- state grant portal identifiers;
- application/status ecosystem understanding;
- awarded-grant records where exposed.

### Georgia OPB Active Grant Programs / Awarded Grants

Use for program and historical award/winner fixtures where available.

### Georgia Department of Community Affairs

Use for agency-specific opportunities/NOFOs.

### GEMA/HS

Use as a second agency-source pattern if relevant.

### Georgia EPD or another domain agency

Use to test heterogeneous source shapes.

## Georgia source-design goal

Prove that source-specific fields normalize into the same Book 2 core domain rather than creating a `GeorgiaGrant` root entity.

## Crawled-state rule

For sources without structured APIs:

```text
Registered source
→ Crawl4AI/browser capture
→ raw snapshot
→ parser/extractor
→ normalized candidate
→ validation/promotion
```

No crawling directly into CanonicalFact.

## Georgia identifier policy

Any portal-specific IDs are stored as namespaced external identifiers.

## Tests

- Georgia opportunity validates as standard GrantOpportunity + OpportunityRevision;
- Georgia award/recipient maps to standard Award + Organization;
- changed webpage generates new snapshot/change event;
- crawler source cannot outrank current official attached solicitation for solicitation terms if contradiction exists.

## Commit

`G0-B3-C15-C17: establish statistics, federal and Georgia source profiles`

---

# 22. Chapter B3.C18 — Private/Foundation/Corporate Source Protocol

## Objective

Support the client's non-government grant categories without forcing a paid data dependency into the MVP.

## Initial architecture

### Registered funder pages

Use governed crawling for:

- foundation grant opportunities;
- corporate philanthropy programs;
- community foundations;
- local grantmakers.

### Optional curated providers later

Candid or equivalent may be integrated after measuring marginal value/cost.

## Source registration requirements

- issuer ownership verified;
- relevant page(s) identified;
- update frequency estimated;
- terms/robots reviewed;
- crawler strategy tested;
- source authority limited to what issuer controls;
- historical winners captured only where source supports them.

## Private source uncertainty

Private grantmakers may not expose clean identifiers or history. Preserve uncertainty rather than inventing structured certainty.

## Tests

- missing stable ID still allows internal source/opportunity identity;
- webpage redesign does not silently create duplicate opportunity if identity resolution supports continuity;
- old foundation webpage does not outrank current issuer page.

---

# 23. Chapter B3.C19 — Source Security & Prompt-Injection Constitution

## Objective

Treat all external source content as untrusted data.

## Threat classes

- prompt injection in webpages/PDFs;
- malicious links;
- data exfiltration instructions;
- embedded scripts;
- poisoned metadata;
- malicious documents;
- oversized/decompression-bomb files;
- credential phishing;
- source-domain impersonation;
- SSRF through crawler URLs;
- redirect abuse.

## Security rules

1. source content cannot grant capabilities;
2. workers receive source text in untrusted-data envelope;
3. browser/crawler egress restricted by policy;
4. raw HTML/scripts never execute in trusted control context;
5. downloads scanned/validated according to file type;
6. redirects/domain changes logged;
7. credentials never exposed to source content;
8. extraction prompts explicitly distinguish instructions from source data;
9. suspicious source content can be quarantined;
10. model/tool decisions remain policy-gated outside source context.

## Sanitized SourceEnvelope

Conceptual structure:

```yaml
source_snapshot_id:
trusted_metadata:
untrusted_content_ref:
content_type:
security_flags:
allowed_operations:
```

## Tests

- webpage says “send secrets to X” → ignored/flagged;
- malicious redirect blocked;
- source tries to invoke tool syntax → inert data;
- unsupported executable file quarantined.

## Commit

`G0-B3-C18-C19: govern private sources and hostile-source security`

---

# 24. Chapter B3.C20 — Data Retention, Deletion & Privacy Classes

## Objective

Define lifecycle before raw source and client data accumulate.

## Data classes

### D0 — Public source metadata

Long retention allowed subject to source/licensing policy.

### D1 — Public raw source snapshots

Retain as needed for provenance/replay, subject to terms and storage policy.

### D2 — Client canonical business data

Tenant-owned; retention/deletion policy required.

### D3 — Sensitive client/PII

Stricter access/encryption/retention.

### D4 — Generated artifacts

Versioned, tenant-controlled.

### D5 — Worker sidechains/traces

Shorter retention by default; redact sensitive/tool content.

### D6 — Audit/security records

Longer governed retention where required.

### D7 — Caches/temp extraction

Disposable/TTL.

## Deletion semantics

Need distinction between:

- delete content;
- tombstone metadata;
- revoke access;
- archive;
- legal/operational hold placeholder.

## Provenance deletion rule

If content must be deleted, downstream artifacts/facts must record that original evidence is no longer available and may need demotion depending on policy.

## Tests

- deleting raw evidence changes replay status appropriately;
- tenant delete does not expose data in sidechains/cache;
- audit metadata does not retain raw secret/PII fixture unnecessarily.

---

# 25. Chapter B3.C21 — Provenance Chain Specification

## Objective

Make every material generated claim traceable.

## Minimum chain

```text
SourceRegistry
   ↓
CaptureEvent / SourceSnapshot
   ↓
ExtractionEvent
   ↓
NormalizationEvent
   ↓
EvidenceClaim / ExternalIdentifier / StatisticObservation
   ↓
PromotionEvent / CanonicalFact
   ↓
EligibilityDecision / MatchExplanation / ResearchFinding
   ↓
RequirementResponse / ProposalSection / BudgetLine
   ↓
ArtifactVersion / SubmissionPackage
```

## ProvenanceEdge

```yaml
edge_id:
from_type:
from_id:
to_type:
to_id:
relationship:
transformation_id:
created_at:
```

## Required relationships

- CAPTURED_FROM;
- EXTRACTED_FROM;
- NORMALIZED_FROM;
- SUPPORTED_BY;
- CONTRADICTED_BY;
- DERIVED_FROM;
- USED_IN;
- SATISFIES;
- GENERATED_FROM;
- SUPERSEDES;
- INVALIDATED_BY.

## Client-visible lineage

Not every internal transformation must be shown in UI, but the product must be able to surface understandable research/source support behind matching and application content.

## Tests

Given a material proposal sentence/assertion, trace to source capture.

Missing critical hop = FAIL.

## Commit

`G0-B3-C20-C21: freeze retention and end-to-end provenance chain`

---

# 26. Chapter B3.C22 — Source Health, Observability & Degradation

## Objective

Treat sources as operational dependencies with measurable health.

## Health states

- HEALTHY;
- DEGRADED;
- FAILING;
- AUTH_ERROR;
- RATE_LIMITED;
- SCHEMA_CHANGED;
- DISABLED;
- UNKNOWN.

## Metrics

- last successful fetch;
- failure rate;
- latency;
- schema-validation rate;
- extraction-quality trend;
- HTTP status distribution;
- rate-limit events;
- content-change frequency;
- duplicate rate;
- stale-source count;
- downstream invalidations.

## Source health policy

A source can remain queryable historically while disabled for fresh promotion.

## Schema drift

If an API response shape changes materially:

```text
schema validation failure
→ source DEGRADED/SCHEMA_CHANGED
→ adapter promotion disabled
→ fixture captured
→ repair/eval required
```

Do not silently map missing fields to null and continue for critical facts.

## Tests

- schema-change fixture triggers degraded state;
- source outage does not erase cached history;
- hard-stale critical opportunity forces uncertainty/block.

---

# 27. Chapter B3.C23 — D0 Shadow Draft Data Packet

## Objective

Unlock the first grounded mock grant immediately after Book 3 ratification.

Book 2 defined the semantic `DraftContextBundle`. Book 3 now defines the **source-governed evidence packet** required to construct one.

## D0 source packet

Must include:

```text
1. Client-profile fixture
   - manually approved
   - fact status clearly labeled

2. Georgia opportunity
   - registered source
   - immutable SourceSnapshot
   - exact OpportunityRevision

3. Opportunity requirements
   - extracted/normalized
   - source-location references

4. Eligibility
   - validated rules
   - deterministic decision
   - evidence refs

5. Funder/program research
   - source-backed
   - research findings with claim refs

6. Historical winner/award research where available
   - official/registered source
   - no unsupported causal inference

7. Georgia/community impact statistics
   - typed StatisticObservations
   - geography/time/vintage explicit

8. Budget assumptions
   - client-provided/verified labels
   - deterministic calculations

9. Proposal profile
   - client 18-section skeleton as template/profile
   - opportunity requirements can alter actual blueprint
```

## D0 output rules

The Shadow Draft Harness may create:

- a full or partial mock proposal;
- optional business-plan excerpt;
- research summary;
- QA/evidence report.

All marked:

```text
MOCK
NON-SUBMISSION
NOT CLIENT-APPROVED FINAL
```

## D0 fact discipline

No missing factual input may be silently invented.

Use explicit placeholders/status:

- NEEDS_CLIENT_INPUT;
- NEEDS_SOURCE;
- PROVISIONAL;
- UNSUPPORTED_DO_NOT_USE.

## D0 success criteria

- exact source revision visible;
- material claims traceable;
- requirement coverage measurable;
- no raw worker/web context required for reconstruction;
- draft can be regenerated from packet.

## Commit

`G0-B3-C22-C23: add source health controls and D0 grounded draft packet`

---

# 28. Chapter B3.C24 — D0 Shadow Draft Harness Specification

## Objective

Specify, but do not yet productionize, the first visible writing demonstration.

## Harness flow

```text
D0 Data Packet
   ↓
Application Blueprint Generator
   ↓
Requirement-to-Section Map
   ↓
Evidence Retrieval from Packet
   ↓
Draft Section Generator
   ↓
Factuality / Citation Check
   ↓
Requirement Coverage Check
   ↓
Cross-Section Consistency
   ↓
Mock Proposal Artifact
   ↓
D0 QA Report
```

## Model permissions

L2 internal only.

No email/send/submission tools.

## Prompt requirements

- use only provided facts/evidence;
- explicitly label unsupported missing inputs;
- separate source-backed fact from narrative framing;
- never manufacture testimonials/partnerships/credentials;
- preserve amount/date/organization names exactly from canonical bundle;
- grant-specific alignment required;
- citations/source refs included in internal draft metadata even if final client rendering uses another citation style.

## Evaluation

D0 is not judged by award rate.

Judge:

- requirement coverage;
- unsupported claim rate;
- evidence lineage completeness;
- factual consistency;
- organization/opportunity correctness;
- usefulness/human review burden;
- reproducibility.

## Hard stop

D0 is an evaluation artifact. It cannot be represented as submission-ready production output.

---

# 29. Chapter B3.C25 — Adversarial Data Test Suite

## A1 — Stale deadline

Cached portal says Sep 15; current official amendment says Sep 29.

Expected: current authoritative value wins; old remains lineage.

## A2 — Equal-authority conflict

Two current official documents disagree.

Expected: CONFLICTED, critical use blocked.

## A3 — Search snippet hallucination

Search result says award amount but original source does not.

Expected: snippet cannot promote claim.

## A4 — Model-generated fake citation

Expected: unavailable/unverified source → claim rejected/provisional.

## A5 — Web prompt injection

Expected: inert/untrusted content; policy unaffected.

## A6 — Parser corrupts table

Raw PDF has $250,000; extraction returns $25,000.

Expected: extraction-quality/validation mismatch prevents verified promotion.

## A7 — API schema drift

Field renamed/removed.

Expected: source DEGRADED, no silent critical nulls.

## A8 — User-provided EIN conflict

Expected: USER_ASSERTED does not outrank verified official ID; identity review.

## A9 — County/city statistic mismatch

Expected: blocked/qualified.

## A10 — Old Census vintage

New official vintage exists but old still used.

Expected: freshness state stale based on latest-vintage policy.

## A11 — Deleted webpage

Historical source disappears.

Expected: retained snapshot supports historical replay subject to retention/terms.

## A12 — Crawler gets redirect to unrelated domain

Expected: blocked/flagged.

## A13 — Duplicate same-content retrieval

Expected: no duplicate bytes; retrieval timing preserved.

## A14 — Material amendment after D0 draft

Expected: D0 packet/draft marked stale and regenerate/review required.

## A15 — Nonmaterial formatting change

Expected: no unnecessary application invalidation.

## A16 — Source adapter self-promotion

Adapter tries to mark extracted claim VERIFIED.

Expected: policy rejects; promotion service governs state.

## A17 — Missing raw snapshot

Normalized critical fact exists but raw source unavailable.

Expected: cannot achieve full verified/replayable status unless explicit governed exception.

## A18 — Cross-tenant source upload

Expected: tenant scoping enforced.

## A19 — Malicious uploaded DOCX/PDF

Expected: quarantine/validation path.

## A20 — Amount units mismatch

Source says thousands but parser interprets dollars.

Expected: normalization validation catches unit discrepancy.

## A21 — Date timezone ambiguity

Expected: unresolved/normalized with source semantics; no silent midnight assumption where material.

## A22 — Private foundation old webpage vs new issuer page

Expected: current issuer source precedence.

## A23 — Historical award inferred as past winner of exact opportunity without proof

Expected: record award relationship at supported level; do not fabricate opportunity linkage.

## A24 — Causal inference from winner cohort

Expected: descriptive analysis allowed; unsupported causality blocked.

## A25 — Retention deletion breaks evidence

Expected: downstream evidence status updated/demoted/replay status changed.

---

# 30. Chapter B3.C26 — Integration, Replay & Property Tests

## Mandatory invariants

```text
1. Every enabled source exists in SourceRegistry.
2. Every material source-derived fact points to a SourceSnapshot.
3. Every raw source capture has integrity identity.
4. SourceSnapshots are immutable.
5. Parsing/extraction is versioned separately from capture.
6. Promotion policy is independent of extraction engine.
7. Search snippets cannot promote critical claims.
8. Source precedence is fact-class-specific.
9. Freshness is fact/source semantic, not generic age.
10. Equal-authority critical conflicts block action.
11. Material changes produce SourceChangeEvents.
12. P0 source changes invalidate dependent decisions/artifacts.
13. External identifiers require verification state.
14. Statistics preserve geography/population/time/vintage.
15. Web/source content has no policy authority.
16. Historical decisions remain replayable against old snapshots.
17. Source health failure cannot silently create false freshness.
18. Retention/deletion state propagates to replay/evidence status.
19. Georgia and federal sources normalize into Book 2 ontology.
20. Private/crawled sources remain governed/registered.
21. D0 packet reconstructs without agent memory.
22. D0 draft can be regenerated from same packet with bounded nondeterministic variance and identical factual inputs.
```

## Property tests

- raw-content hashing idempotent;
- precedence resolver deterministic for same policy/input;
- freshness resolver deterministic for same clocks/vintage;
- dependency invalidation deterministic;
- provenance graph has no orphan material facts;
- replay transformations preserve referenced source identities.

---

# 31. Chapter B3.C27 — Book 3 Reality Lock

## Machine-readable report

```json
{
  "book": "G0-B3",
  "status": "PASS|FAIL",
  "data_constitution_complete": true,
  "enabled_sources_registered": 1.0,
  "critical_facts_with_snapshot_lineage": 1.0,
  "snapshot_immutability_tests_pass": true,
  "capture_replay_tests_pass": true,
  "extraction_lineage_tests_pass": true,
  "precedence_tests_pass": true,
  "freshness_tests_pass": true,
  "promotion_tests_pass": true,
  "conflict_tests_pass": true,
  "material_change_tests_pass": true,
  "dependency_invalidation_tests_pass": true,
  "identifier_verification_tests_pass": true,
  "statistic_semantics_tests_pass": true,
  "source_security_tests_pass": true,
  "retention_tests_pass": true,
  "provenance_chain_tests_pass": true,
  "federal_fixture_tests_pass": true,
  "georgia_fixture_tests_pass": true,
  "private_source_fixture_tests_pass": true,
  "d0_data_packet_ready": true,
  "d0_shadow_draft_allowed": true,
  "adversarial_p0_pass": true,
  "p0_open": 0,
  "ready_for_d0": true,
  "ready_for_book4": true
}
```

`ready_for_d0` and `ready_for_book4` must be computed from evidence.

---

# 32. Commit Plan

The execution agent should work continuously and commit at these coherent boundaries:

```text
1. G0-B3-C1
   data constitution

2. G0-B3-C2-C3
   source classification + SourceRegistry

3. G0-B3-C4-C5
   onboarding + immutable SourceSnapshot

4. G0-B3-C6-C7
   capture/replay + extraction/normalization

5. G0-B3-C8-C9
   precedence + freshness

6. G0-B3-C10-C12
   promotion + conflicts + source change

7. G0-B3-C13-C14
   dependency invalidation + identifier verification

8. G0-B3-C15-C17
   statistics + federal + Georgia source profiles

9. G0-B3-C18-C19
   private sources + hostile-source security

10. G0-B3-C20-C21
    retention + provenance chain

11. G0-B3-C22-C24
    source health + D0 data packet + D0 harness specification

12. G0-B3-C25-C26
    adversarial + integration/replay/property tests

13. G0-B3-BOOK
    complete Book 3 evidence packet

14. G0-B3-REPAIR-1...N
    bounded review repairs

15. G0-B3-RATIFY
    pass Book 3 Reality Lock / unlock D0 + Book 4
```

The agent must stop only for a genuine P0 contradiction, legal/access ambiguity requiring client/operator decision, or source dependency whose terms/license make the planned architecture invalid.

---

# 33. Parallel-Agent Work Allocation

Book 3 is suitable for multiple agents, but ownership boundaries matter.

## Lane A — Data Constitution / Source Registry

Owns:

- C1 Constitution;
- C2 Classification;
- C3 Registry;
- C4 Onboarding.

This lane lands first.

## Lane B — Capture / Replay / Parsing

After SourceSnapshot core agreed:

- C5 Snapshot;
- C6 Capture/Replay;
- C7 Extraction/Normalization.

## Lane C — Trust / Freshness / Conflict

After C1–C3:

- C8 Precedence;
- C9 Freshness;
- C10 Promotion;
- C11 Conflict;
- C12 Change;
- C13 Invalidation.

## Lane D — Evidence Types / Source Profiles

- C14 identifiers;
- C15 statistics;
- C16 federal profiles;
- C17 Georgia profiles;
- C18 private sources.

## Lane E — Security / Retention / Provenance

- C19 hostile-source security;
- C20 retention;
- C21 provenance;
- C22 health/observability.

## Lane F — D0 / Testing

After core contracts stabilize:

- C23 D0 packet;
- C24 Shadow Draft Harness spec;
- C25 adversarial;
- C26 integration/replay/property tests;
- C27 Reality Lock.

## Merge rule

Only Lane A/Data Constitution owner may change source-law semantics without ADR. Only Book 2 amendment may change core entity meaning. Test lane may identify defects but must not silently rewrite source/trust policy.

---

# 34. Allowed / Prohibited Paths

## Allowed

- Book 3 docs;
- data/source schemas;
- source registry config;
- fixture-backed data prototypes;
- captured test fixtures that comply with source/licensing/privacy rules;
- provenance/freshness/conflict prototypes;
- D0 mock harness specification and non-production evaluation harness if explicitly allowed by branch policy;
- tests/evidence/ADRs.

## Prohibited

- production grant submission;
- production external email/outreach;
- uncontrolled live crawling;
- storing credentials in repo;
- final production secrets/auth system (Book 6);
- redefining Book 2 entities;
- implementing Hermes memory protocol (Book 4);
- selecting final evidence storage backend (Book 5) beyond backend-neutral contracts;
- turning crawler/parser libraries into canonical authority;
- importing trading/OCE unrelated code.

---

# 35. Definition of Done

Book 3 is complete only when:

1. Data Constitution is ratifiable and machine-referenced;
2. source classes and authority tiers are defined;
3. SourceRegistry schema and onboarding protocol exist;
4. SourceSnapshot/capture semantics are immutable and replayable;
5. extraction and normalization are versioned separately;
6. precedence rules exist for critical fact classes;
7. freshness policy distinguishes opportunity/statistic/organization/history semantics;
8. promotion confidence is decomposed and policy-driven;
9. conflict states/resolution are explicit;
10. source changes have materiality classification;
11. dependency invalidation is selective/testable;
12. external identifiers have source-backed verification state;
13. statistics preserve geography/population/time/methodology;
14. federal source profiles are defined;
15. Georgia source profiles are defined as first state proof;
16. private/foundation source path is defined without mandatory paid provider;
17. hostile-source/prompt-injection policy is explicit;
18. retention/deletion classes exist;
19. provenance chain is end-to-end traceable;
20. source health/schema-drift behavior exists;
21. federal/Georgia/private fixtures pass;
22. D0 source-governed data packet is complete;
23. Shadow Draft Harness specification exists;
24. adversarial P0 tests pass;
25. Reality Lock outputs `ready_for_d0=true` and `ready_for_book4=true`.

---

# 36. D0 Execution Handoff

Immediately after Book 3 ratification, the project may execute the first **Shadow Draft** before Book 4 is complete.

Recommended D0 execution sequence:

```text
1. Choose one real Georgia opportunity with manageable requirements.
2. Capture/register exact source revision.
3. Build manual approved client-profile fixture.
4. Normalize eligibility + requirements.
5. Gather 2–5 strong funder/winner/community evidence sources as applicable.
6. Build typed D0 Data Packet.
7. Generate application blueprint.
8. Generate full or selected proposal sections.
9. Run requirement/factuality/citation/consistency QA.
10. Produce Mock Proposal + Research Pack + QA Report.
11. Review with client/operator.
12. Feed discovered ontology/data gaps back as repair evidence before/while Book 4 proceeds.
```

This creates the first client-visible grant-writing value without compromising authority, source lineage or submission controls.

The D0 result is not considered production proof; it is a controlled product-direction/evaluation artifact.

---

# 37. Precise Handoff to Book 4

Book 4 receives a fully defined world:

```text
WHO MAY ACT             ← Book 1
WHAT OBJECTS MEAN       ← Book 2
HOW REALITY ENTERS      ← Book 3
```

Book 4 then defines:

> How does Personal Hermes convert conversation into intent, how does CEO Hermes consume only the necessary canonical/evidence context, how are worker tasks isolated, how are results returned, and how does memory retain useful continuity without becoming truth?

Book 4 receives:

- registered source identities;
- snapshot/provenance semantics;
- fact/claim/statistic states;
- conflict/freshness states;
- exact domain object identities/revisions;
- D0 DraftContextBundle/Data Packet;
- source security envelope;
- audit/provenance expectations.

Therefore Hermes does not need to “remember” where facts came from. It gets references into governed canonical/evidence state.

---

# 38. Book 3 North-Star Test

At the end of Book 3, pick any material sentence proposed for a grant application—such as an organization credential, deadline, funding limit, community statistic or historical award—and ask:

```text
What exactly is this claim?
Which canonical entity does it concern?
Which source asserted it?
What raw source did we capture?
When did we retrieve it?
When was it effective?
Which parser/extractor produced the structured value?
Which normalizer mapped it?
How authoritative is that source for this fact class?
Is it fresh enough for this use?
Does anything contradict it?
Was it promoted or only provisional?
What decisions/artifacts currently depend on it?
What happens if the source changes tomorrow?
Can we replay the chain without Hermes memory?
```

If the system cannot answer those questions deterministically and with lineage, Book 3 is not finished.