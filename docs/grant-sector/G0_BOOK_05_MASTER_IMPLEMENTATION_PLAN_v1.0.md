# G0 Book 5 — Evidence, Provenance & Decision Substrate Master Implementation Plan

**Document ID:** GS-G0-B5-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR CONTINUOUS EXECUTION AFTER BOOK 4 RATIFICATION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Receives from:** Books 0–4  
**Hands off to:** Book 6 Security, Identity & Tool Authority; Book 7 Evaluation; Book 8 Vertical Slice

---

# 0. Book Mission

Book 5 defines and proves the substrate that answers:

> Why does the system believe this, where did it come from, what contradicted it, what was known when a decision was made, which downstream outputs depended on it, and can the decision be replayed later?

Books 2 and 3 defined domain meaning and how external reality enters the platform. Book 4 defined how agents consume bounded context without making memory canonical. Book 5 turns those contracts into a durable **evidence and decision fabric**.

This is deliberately not “pick a graph database.” The substrate must be storage-implementation-independent at the contract layer. Semantica, relational PostgreSQL, graph projections, vector retrieval, or hybrids are implementation candidates—not constitutional truth.

Book 5 must prevent:

- a proposal claim with no recoverable source lineage;
- a match score that cannot be reconstructed;
- eligibility evaluated against unknown facts/revisions;
- an agent explanation that cites evidence different from what the decision used;
- contradiction resolution deleting the losing evidence;
- graph convenience becoming a second canonical database;
- vector similarity becoming factual authority;
- Semantica or another framework owning sovereign domain identity;
- generated text becoming evidence merely because another model repeated it;
- source amendments leaving stale drafts looking current;
- evaluation datasets losing the exact decision context they were derived from.

---

# 1. Book Theme

## Evidence → Lineage → Contradiction → Decision → Dependency → Replay → Retrieval → Projection

```text
BOOK 2 SEMANTICS
+
BOOK 3 SOURCE/SNAPSHOT TRUTH
+
BOOK 4 CONTEXT CONTRACTS
        ↓
EVIDENCE OBJECTS
        ↓
PROVENANCE EDGES
        ↓
CLAIM / FACT SUPPORT GRAPH
        ↓
DECISION RECORDS
        ↓
DEPENDENCY GRAPH
        ↓
TEMPORAL REPLAY
        ↓
RETRIEVAL / EXPLANATION
        ↓
OPTIONAL GRAPH / SEMANTICA PROJECTION
```

The graph is a **semantic relationship model** first. Physical graph storage is optional.

---

# 2. Hard Inputs from Previous Books

Book 5 inherits these non-negotiable constraints:

1. agent memory is not canonical truth;
2. stable internal IDs are sovereign over provider IDs;
3. SourceSnapshots are immutable evidence anchors;
4. EvidenceClaim and CanonicalFact are distinct;
5. contradictory claims remain visible;
6. material source changes invalidate dependent state;
7. OpportunityRevision is exact and immutable;
8. EligibilityDecision is deterministic after rule normalization;
9. ApplicationProject and artifacts retain revision lineage;
10. statistics preserve geography/population/reference-period context;
11. workers are bounded and traces stay out of parent context;
12. critical operations must be replayable without hidden model history;
13. consequential actions are auditable;
14. tenant isolation applies to evidence and derived graph relationships;
15. safe drafting remains L2; submission remains disabled;
16. generated prose cannot promote itself to evidence;
17. client-visible research is a product obligation;
18. future learning/self-improvement consumes evidence but cannot silently rewrite doctrine.

If the evidence substrate cannot satisfy these without redefining earlier semantics, issue an amendment rather than creating shadow concepts.

---

# 3. Book 5 Design Philosophy

## 3.1 Provenance is a product primitive

Lineage is not debug metadata. It supports factuality, user trust, review, change invalidation, audits, evaluation and later learning.

## 3.2 Canonical state and graph projections are different

Canonical domain state remains in the governed system of record. A graph/index may project it for traversal and retrieval.

## 3.3 Append history; do not rewrite history

Corrections create supersession/resolution events. They do not erase what the system previously observed or believed.

## 3.4 Decisions are first-class records

Do not store only final answers. Persist the exact inputs, versions, policy/evaluator version, result and explanation lineage required for replay.

## 3.5 Retrieval does not equal authority

Search rank, vector similarity, graph proximity and model confidence are discovery signals. Authority comes from source/evidence/promotion policy.

## 3.6 Evidence quality is multidimensional

Authority, freshness, directness, specificity, corroboration and extraction quality are separate dimensions. Avoid one magical confidence score that hides why evidence is strong or weak.

## 3.7 Contradictions are state, not exceptions

The system must represent disagreement explicitly.

## 3.8 Temporal correctness matters

The question is often not “what is true now?” but “what evidence and rules were in force when this draft/decision was created?”

## 3.9 The client must be able to inspect important reasoning

Do not expose chain-of-thought. Expose structured evidence, requirement coverage, decision inputs, citations, conflicts, assumptions and outcome summaries.

## 3.10 Optional frameworks must be replaceable

Semantica or any graph/RAG framework must sit behind adapters and pass an exit test.

---

# 4. Required Artifact Set

```text
docs/grant-sector/g0/05-evidence/
├── G0_B5_EVIDENCE_CONSTITUTION.md
├── G0_B5_PROVENANCE_MODEL.md
├── G0_B5_EVIDENCE_GRAPH_SEMANTICS.md
├── G0_B5_DECISION_RECORD_CONTRACT.md
├── G0_B5_TEMPORAL_REPLAY_CONTRACT.md
├── G0_B5_CONTRADICTION_RESOLUTION_MODEL.md
├── G0_B5_DEPENDENCY_INVALIDATION_MODEL.md
├── G0_B5_EVIDENCE_QUALITY_MODEL.md
├── G0_B5_RETRIEVAL_CONSTITUTION.md
├── G0_B5_CLIENT_EXPLANATION_CONTRACT.md
├── G0_B5_SEMANTICA_BAKEOFF_PLAN.md
├── G0_B5_SEMANTICA_BAKEOFF_RESULTS.md
├── G0_B5_STORAGE_DECISION_ADR.md
├── G0_B5_GRAPH_PROJECTION_CONTRACT.md
├── G0_B5_VECTOR_INDEX_CONTRACT.md
├── G0_B5_AUDIT_EVIDENCE_LINKAGE.md
├── G0_B5_EVAL_DATASET_LINEAGE.md
├── G0_B5_D0_D1_EVIDENCE_READINESS.md
├── G0_B5_ADVERSARIAL_TEST_REPORT.md
├── G0_B5_PERFORMANCE_TEST_REPORT.md
├── G0_B5_REALITY_LOCK_REPORT.md
└── G0_B5_HANDOFF_TO_BOOK_6.md

schemas/g0/evidence/
├── provenance_ref.schema.json
├── evidence_edge.schema.json
├── support_assertion.schema.json
├── contradiction.schema.json
├── resolution_event.schema.json
├── decision_record.schema.json
├── decision_input_ref.schema.json
├── dependency_edge.schema.json
├── invalidation_event.schema.json
├── evidence_quality.schema.json
├── retrieval_result.schema.json
├── explanation_packet.schema.json
├── graph_projection_event.schema.json
└── eval_case_lineage.schema.json

config/g0/evidence/
├── evidence_edge_types.yaml
├── evidence_quality_dimensions.yaml
├── contradiction_types.yaml
├── decision_types.yaml
├── invalidation_rules.yaml
├── retrieval_policies.yaml
└── projection_policies.yaml

prototype/g0/evidence/
├── models.py
├── provenance.py
├── decisions.py
├── replay.py
├── contradictions.py
├── dependencies.py
├── retrieval.py
├── projections.py
├── semantica_adapter.py
└── fixtures/

tests/g0/book5/
├── test_provenance_graph.py
├── test_decision_records.py
├── test_temporal_replay.py
├── test_contradictions.py
├── test_dependency_invalidation.py
├── test_evidence_quality.py
├── test_retrieval_authority.py
├── test_graph_projection.py
├── test_semantica_adapter.py
├── test_semantica_exit.py
├── test_eval_lineage.py
├── test_tenant_isolation.py
└── test_adversarial_evidence.py
```

---

# 5. Chapter B5.C1 — Evidence Constitution

## Objective

Freeze the laws governing evidence and decisions.

## Required laws

### EVID-LAW-001 — Every material operational claim must be lineage-capable

A material factual claim used in eligibility, matching, drafting, budget, readiness or explanation must trace to evidence or be explicitly labeled assumption/user assertion/unknown.

### EVID-LAW-002 — Generated text is not evidence

Model output can propose claims or synthesize evidence. It cannot become evidence solely through generation.

### EVID-LAW-003 — Evidence retains source identity

Normalization does not sever SourceSnapshot/extraction lineage.

### EVID-LAW-004 — Promotion is explicit

Claim→CanonicalFact requires a governed promotion/resolution event.

### EVID-LAW-005 — Contradictory evidence is retained

Resolution does not delete the losing claim.

### EVID-LAW-006 — Decisions pin exact inputs

Decision records reference exact revisions/versions used.

### EVID-LAW-007 — Replay uses historical state

Replaying a historical decision must not silently substitute current facts/sources.

### EVID-LAW-008 — Retrieval is non-authoritative

Retrieved content must still pass evidence/policy checks.

### EVID-LAW-009 — Derived claims retain derivation lineage

Calculations and transformations identify upstream evidence and deterministic method/version.

### EVID-LAW-010 — Evidence is tenant scoped where applicable

No cross-tenant evidence leakage through graph/vector/retrieval layers.

### EVID-LAW-011 — Public evidence and private client evidence remain distinguishable

Visibility and sharing policy must be explicit.

### EVID-LAW-012 — Explanation must reflect decision evidence

User-facing explanation cannot cite a convenient source that was not part of or compatible with the actual decision basis.

### EVID-LAW-013 — Material amendments trigger dependency review

The evidence graph must support selective invalidation.

### EVID-LAW-014 — Confidence cannot override hard contradiction

A high similarity/model score cannot silently resolve conflicting authoritative evidence.

### EVID-LAW-015 — Physical storage is replaceable

No external framework owns canonical entity identity or constitutional semantics.

## Commit

`G0-B5-C1: freeze evidence and decision constitutional laws`

---

# 6. Chapter B5.C2 — Provenance Reference Model

## Objective

Create one common reference vocabulary for tracing data and outputs.

## ProvenanceRef

Conceptual shape:

```yaml
ref_id:
ref_type:
entity_type:
entity_id:
version_or_revision_id:
tenant_id:
content_hash:
observed_at:
effective_at:
locator:
```

`ref_type` examples:

- SOURCE_SNAPSHOT;
- EXTRACTION_EVENT;
- NORMALIZATION_EVENT;
- EVIDENCE_CLAIM;
- CANONICAL_FACT;
- STATISTIC_OBSERVATION;
- ELIGIBILITY_RULE;
- ELIGIBILITY_DECISION;
- MATCH_DECISION;
- REQUIREMENT;
- RESEARCH_FINDING;
- BUDGET_VERSION;
- ARTIFACT_VERSION;
- QA_RESULT;
- POLICY_DECISION;
- HUMAN_APPROVAL;
- OUTCOME_FEEDBACK.

## Locator

A provenance ref may include a locator into a source/artifact:

```text
URL + snapshot hash
PDF page
HTML selector
JSON pointer
CSV row/key
spreadsheet cell/range
text span
section ID
```

Locators aid review but do not replace immutable snapshot identity.

## Tests

- every supported ref resolves to typed object or explicit tombstone;
- hash mismatch detected;
- tenant mismatch rejected;
- locator can be absent only when object-level evidence is sufficient.

---

# 7. Chapter B5.C3 — Evidence Graph Semantics

## Objective

Define graph meaning independent of graph technology.

## Node families

Nodes are projections/references to Book 2/3/4 objects, not duplicate sovereign entities.

Core families:

```text
SourceSnapshot
ExtractionEvent
EvidenceClaim
CanonicalFact
StatisticObservation
Organization
Program
GrantOpportunity
OpportunityRevision
Requirement
EligibilityRule
EligibilityDecision
MatchDecision
ResearchFinding
ApplicationProject
BudgetVersion
ArtifactVersion
QAResult
PolicyDecision
HumanApproval
OutcomeFeedback
```

## Edge families

### Source lineage

- EXTRACTED_FROM
- NORMALIZED_FROM
- OBSERVED_IN
- DERIVED_FROM

### Evidence semantics

- SUPPORTS
- CONTRADICTS
- CORROBORATES
- SUPERSEDES
- QUALIFIES
- MEASURES

### Decision lineage

- DECISION_USED
- DECISION_PRODUCED
- EVALUATED_AGAINST
- EXPLAINED_BY

### Application lineage

- REQUIREMENT_SATISFIED_BY
- ARTIFACT_USES
- BUDGET_SUPPORTS
- QA_CHECKED
- REVIEWED_BY

### Dependency semantics

- DEPENDS_ON
- INVALIDATES
- REQUIRES_RECOMPUTE

## Edge contract

```yaml
edge_id:
edge_type:
from_ref:
to_ref:
tenant_scope:
created_at:
created_by:
method:
confidence_dimensions:
valid_from:
valid_to:
status:
```

## Hard rule

Edges cannot create facts that do not exist in the governed domain/evidence layer.

## Tests

- invalid endpoint combinations rejected;
- duplicate semantic edges idempotent where appropriate;
- cross-tenant edges denied;
- deletion/tombstone does not silently orphan historical decision replay.

## Commit

`G0-B5-C2-C3: define provenance references and evidence graph semantics`

---

# 8. Chapter B5.C4 — Evidence Quality Model

## Objective

Replace vague confidence with inspectable dimensions.

## Dimensions

### Authority

How authoritative is the source for this claim?

### Directness

Primary statement/data vs secondary report vs inferred/derived.

### Freshness

How current is the evidence relative to claim type?

### Specificity

Does evidence address the exact entity/geography/program/time period?

### Corroboration

Independent supporting sources.

### Extraction quality

Structured API vs clean table vs parsed PDF vs uncertain extraction.

### Identity certainty

Confidence that evidence refers to the correct entity.

### Temporal fit

Does evidence apply to the relevant effective period?

## Representation

Each dimension must remain inspectable. A composite score may exist for ranking but cannot erase component values.

## Quality classes

Suggested:

- VERIFIED_HIGH;
- VERIFIED_MODERATE;
- PROVISIONAL;
- CONFLICTED;
- STALE;
- UNSUPPORTED.

Class rules must be deterministic/configured where possible.

## Tests

- high authority + stale is not silently “high confidence”;
- low extraction quality visible;
- conflicting authoritative sources cannot be averaged away;
- composite score reproducible.

---

# 9. Chapter B5.C5 — Claim Support & Promotion Semantics

## Objective

Specify how evidence supports operational facts without conflating observation and belief.

## SupportAssertion

```yaml
support_id:
claim_ref:
evidence_ref:
support_type:
quality:
created_at:
method:
```

Support types:

- DIRECT;
- CORROBORATING;
- DERIVED;
- USER_ATTESTED;
- ADMIN_VERIFIED;
- OFFICIAL_RECORD;
- STATISTICAL_CONTEXT.

## Promotion event

Promotion must record:

```text
candidate claim
support set
contradiction set
policy/version
actor
result
canonical fact/version
reason codes
```

## Derived facts

Example:

```text
Budget line totals
→ deterministic calculation vX
→ derived fact
```

The derivation method is evidence lineage.

## Tests

- unsupported claim cannot promote under policies requiring support;
- same support cannot masquerade as independent corroboration;
- user-attested and official-record evidence remain distinguishable;
- derived fact replay reproduces value.

---

# 10. Chapter B5.C6 — Contradiction & Resolution Model

## Objective

Make disagreement explicit and recoverable.

## Contradiction object

```yaml
contradiction_id:
subject_scope:
predicate:
claim_refs:
contradiction_type:
severity:
status:
opened_at:
resolved_at:
resolution_event_ref:
```

## Types

- VALUE_CONFLICT;
- IDENTITY_CONFLICT;
- TEMPORAL_CONFLICT;
- SOURCE_REVISION_CONFLICT;
- SCOPE_CONFLICT;
- UNIT_CONFLICT;
- INTERPRETATION_CONFLICT.

## Resolution statuses

- OPEN;
- RESOLVED_SOURCE_PRECEDENCE;
- RESOLVED_TEMPORAL;
- RESOLVED_HUMAN;
- RESOLVED_CORROBORATION;
- SUPERSEDED;
- UNRESOLVED_ACCEPTED.

## ResolutionEvent

Must preserve:

- all conflicting claims;
- chosen operational fact if any;
- policy/reason;
- actor/approval;
- time;
- downstream invalidation.

## Hard rule

“Pick the higher confidence model output” is not a valid universal resolution policy.

## Tests

- equal-authority conflict remains open;
- newer source does not automatically win when historical effective dates differ;
- unit mismatch recognized before value conflict;
- human resolution audited;
- losing claim retained.

## Commit

`G0-B5-C4-C6: implement evidence quality, promotion and contradiction contracts`

---

# 11. Chapter B5.C7 — Decision Record Contract

## Objective

Make every material system decision reconstructable.

## DecisionRecord

```yaml
decision_id:
decision_type:
tenant_id:
project_id:
actor_ref:
capability_id:
created_at:
effective_at:
input_refs:
configuration_refs:
model_or_engine_ref:
policy_ref:
result:
reason_codes:
explanation_data:
output_refs:
status:
supersedes_decision_id:
```

## Decision types

At minimum:

- ELIGIBILITY;
- MATCH_RANKING;
- FACT_PROMOTION;
- CONFLICT_RESOLUTION;
- REQUIREMENT_COVERAGE;
- BUDGET_VALIDATION;
- QA_FACTUALITY;
- QA_ALIGNMENT;
- SUBMISSION_READINESS;
- MEMORY_PROMOTION;
- CHANGE_PROMOTION;
- POLICY_AUTHORIZATION.

## LLM decisions

If an LLM participates, record:

- model/provider/version identifier where available;
- prompt/template version or instruction bundle ref;
- structured input artifact refs;
- structured output hash/ref;
- evaluator/validator refs.

Do not store hidden chain-of-thought as required replay state.

## Tests

- decision missing exact opportunity revision fails validation;
- deterministic decision records engine version;
- model-assisted decision pins structured context refs;
- supersession does not mutate old decision.

---

# 12. Chapter B5.C8 — Temporal Replay Contract

## Objective

Answer “what did the system know and why did it decide X at time T?”

## Replay modes

### HISTORICAL_EXACT

Use the exact pinned inputs/configurations available to the original decision.

### HISTORICAL_REEVALUATE

Use historical evidence but current evaluator/policy to compare behavior.

### CURRENT_REEVALUATE

Use current evidence and current evaluator to assess whether the old decision remains valid.

These must never be conflated.

## Replay packet

```text
DecisionRecord
+
all pinned input refs
+
configuration/policy refs
+
source snapshot refs
+
engine/model metadata
→ ReplayResult
```

## Non-deterministic model caveat

Exact token-for-token LLM regeneration may not be possible. Replay correctness therefore focuses on reconstructing the exact evidence/context/instruction/output artifacts and rerunning validators/evaluators where applicable.

## Tests

- current source update cannot alter HISTORICAL_EXACT inputs;
- deterministic eligibility replay exact;
- historical draft can identify evidence it originally used;
- missing historical dependency is P0 integrity failure.

---

# 13. Chapter B5.C9 — Dependency Graph & Selective Invalidation

## Objective

Turn Book 3 material source changes into targeted recomputation.

## DependencyEdge

```yaml
dependency_id:
dependent_ref:
depends_on_ref:
dependency_type:
materiality:
created_at:
status:
```

## Dependency types

- FACTUAL;
- ELIGIBILITY;
- REQUIREMENT;
- MATCH;
- NUMERIC;
- CITATION;
- NARRATIVE_ALIGNMENT;
- POLICY;
- MODEL_OUTPUT;
- ARTIFACT_BUNDLE.

## InvalidationEvent

Records:

- changed upstream ref;
- change class;
- affected downstream refs;
- required action;
- priority;
- resolved status.

## Selective behavior examples

Deadline change:

```text
OpportunityRevision
→ eligibility timing check
→ requirement deadline
→ readiness
→ user alert/explanation
```

Community statistic update:

```text
StatisticObservation
→ affected proposal sections/research report
```

Formatting-only source change:

```text
SourceSnapshot changed
→ no downstream semantic invalidation if normalized meaning unchanged
```

## Tests

- no global recompute when dependency subset known;
- transitive invalidation bounded and inspectable;
- cycles handled safely;
- stale dependency prevents false submission-ready state.

## Commit

`G0-B5-C7-C9: define decision replay and selective invalidation substrate`

---

# 14. Chapter B5.C10 — Retrieval Constitution

## Objective

Define how agents/services retrieve evidence without confusing relevance with truth.

## Retrieval lanes

### Exact structured lookup

For IDs, canonical facts, current opportunity revision, requirements, decisions.

### Filtered relational retrieval

For scoped entity/project/evidence queries.

### Graph traversal

For lineage, dependencies, contradiction neighborhoods, award/funder relationships.

### Full-text retrieval

For source/artifact text.

### Vector semantic retrieval

For discovery/similarity, not authority.

## Query planning rule

Use the most deterministic lane that can answer the question.

Do not vector-search an EIN, deadline or canonical amount when exact lookup exists.

## RetrievalResult

Must include:

```text
result refs
retrieval method
query scope
ranking metadata
source/evidence quality metadata
staleness/conflict flags
tenant scope
```

## Authority rule

A top-ranked semantic result may be excluded from operational use if evidence policy rejects it.

## Tests

- exact lookup preferred for identifiers;
- vector result cannot override canonical fact;
- stale/conflicted evidence flagged;
- tenant filters applied before retrieval result exposure.

---

# 15. Chapter B5.C11 — Vector Index Contract

## Objective

Use embeddings safely as disposable retrieval infrastructure.

## Rules

1. vectors are derived indexes, never canonical truth;
2. every vector points back to stable source/artifact/evidence ref;
3. embedding model/version recorded;
4. re-embedding does not change source identity;
5. deleted/restricted tenant content is removed/hidden according to retention policy;
6. no cross-tenant similarity search by default;
7. vector metadata includes visibility and evidence class;
8. vector index can be rebuilt from canonical artifacts/snapshots.

## Tests

- full vector-store loss is recoverable;
- embedding model swap does not alter domain IDs;
- stale vector cannot expose deleted tenant artifact;
- search result resolves to canonical provenance ref.

---

# 16. Chapter B5.C12 — Graph Projection Contract

## Objective

Permit graph-native traversal without surrendering canonical state.

## ProjectionEvent

```yaml
projection_event_id:
source_refs:
projection_target:
projection_schema_version:
created_at:
status:
```

## Projection rules

- graph node IDs derive from internal canonical IDs;
- projection is rebuildable;
- graph-only mutation cannot create canonical facts;
- canonical changes propagate through projection events;
- projection lag is measurable;
- graph deletion cannot erase canonical history;
- schema/version mapping explicit.

## Exit test

Delete the graph projection and rebuild it from canonical state/evidence without semantic loss.

If impossible, the graph has accidentally become sovereign and Book 5 fails.

---

# 17. Chapter B5.C13 — Semantica Bake-Off Charter

## Objective

Decide whether `semantica-agi/semantica` earns a place in the architecture through evidence rather than enthusiasm.

## Candidate roles to test

Semantica may be evaluated for:

- evidence/knowledge graph representation;
- provenance traversal;
- entity/relation extraction support;
- semantic retrieval;
- graph-enhanced RAG;
- temporal/relationship queries;
- visualization/debug support.

It must not automatically own:

- canonical organization/opportunity identity;
- Book 2 ontology sovereignty;
- Book 3 SourceSnapshot truth;
- Book 1 authority policy;
- Hermes memory truth;
- production submission state.

## Baseline architecture

Minimum baseline should use the project's existing relational/system-of-record approach plus simple explicit evidence/dependency tables and optional standard retrieval components.

The comparison is not “Semantica vs nothing.” It is:

```text
BASELINE EXPLICIT SUBSTRATE
vs
BASELINE + SEMANTICA ADAPTER/PROJECTION
```

## Bake-off workloads

### W1 — Claim lineage

Given proposal claim, return exact SourceSnapshot/locator chain.

### W2 — Contradiction neighborhood

Find all claims/facts contradicting deadline/eligibility fact.

### W3 — Dependency invalidation

Given amended opportunity fact, identify affected decisions/artifacts.

### W4 — Historical award intelligence

Traverse funder→program→award→recipient relationships.

### W5 — Draft evidence retrieval

Retrieve evidence relevant to a requirement while respecting tenant/source quality.

### W6 — Temporal replay support

Recover evidence neighborhood used by historical decision.

### W7 — Rebuild/exit

Remove Semantica state and reconstruct from canonical substrate.

### W8 — Multi-tenant isolation

Prove no cross-tenant graph/retrieval leakage.

### W9 — Schema evolution

Change an extension/edge type and measure migration complexity.

### W10 — Operational degradation

Semantica unavailable: can core application continue in degraded mode?

## Metrics

Score 1–5 plus measured evidence where possible:

- semantic fit;
- provenance fidelity;
- temporal support;
- query expressiveness;
- developer ergonomics;
- operational complexity;
- latency;
- memory/storage overhead;
- observability;
- multi-tenancy support;
- schema evolution;
- rebuildability;
- lock-in/exit cost;
- license/dependency risk;
- testability;
- failure isolation.

## Decision outcomes

- ADOPT_CORE_PROJECTION;
- ADOPT_OPTIONAL_ACCELERATOR;
- ADOPT_RESEARCH_ONLY;
- DEFER;
- REJECT.

No adoption without completed results artifact and ADR.

## Commit

`G0-B5-C10-C13: freeze retrieval, projection and Semantica bake-off contracts`

---

# 18. Chapter B5.C14 — Storage Decision ADR

## Objective

Ratify the physical evidence substrate after the bake-off.

## Candidate patterns

### Pattern A — Relational canonical + relational evidence/dependency tables

Simplest operationally.

### Pattern B — Relational canonical + graph projection

Canonical truth in relational store; graph optimized for traversal.

### Pattern C — Relational canonical + Semantica-managed projection/index

Only if bake-off justifies it.

### Pattern D — Event-oriented provenance ledger + relational materialization + optional graph

Potentially strongest replay model but higher complexity.

## Decision criteria weighting

Suggested priorities:

```text
Correctness / provenance fidelity       20%
Replayability                           15%
Tenant/security isolation               15%
Replaceability / exit                   10%
Operational simplicity                  10%
Query capability                        10%
Performance                             5%
Developer ergonomics                    5%
Observability                           5%
Cost                                    5%
```

Weights may change only with recorded rationale.

## Hard gate

No candidate can win by aggregate score if it fails:

- tenant isolation;
- historical replay;
- canonical-ID preservation;
- rebuild/exit;
- provenance integrity.

---

# 19. Chapter B5.C15 — Client Explanation Packet

## Objective

Convert evidence/decision lineage into useful transparency without exposing internal chain-of-thought.

## ExplanationPacket

May contain:

```text
Decision/result summary
Why this grant matched
Eligibility status + rule results
Key evidence/citations
Known conflicts/uncertainties
Requirements covered/missing
Budget checks
Research findings
Opportunity revision/date
Source freshness indicators
What changed since prior version
Human review items
```

## Grant-writing example

Instead of:

> “The AI thinks this is a strong grant.”

Provide:

```text
Match: Strong
Eligibility: Eligible on 8/8 validated hard rules
Deadline: Oct 15, 2026 — official opportunity revision 3
Funding range: $50k–$150k
Alignment drivers:
- Georgia service geography
- eligible nonprofit status
- youth workforce program fit
- documented target-population need

Open issue:
- partnership letter still required

Research used:
- official opportunity
- historical award records
- Georgia/community statistics
```

## Rule

Explanations cite structured decision evidence, not hidden reasoning traces.

## Tests

- explanation matches DecisionRecord;
- conflicts are not hidden;
- stale evidence indicated;
- unsupported rationale rejected.

---

# 20. Chapter B5.C16 — Application Claim Ledger

## Objective

Make grant drafts auditable at the claim level without requiring every adjective to be cited.

## Material claim classes

- organization legal/status claims;
- program history/performance;
- population/community statistics;
- funding amounts;
- dates/deadlines;
- partnership claims;
- testimonial/support claims;
- budget assumptions;
- measurable outcomes presented as historical facts;
- prior award/winner claims;
- regulatory/compliance assertions.

## ClaimLedgerEntry

```yaml
artifact_version_id:
section_id:
claim_id:
claim_text_or_structured_ref:
claim_class:
evidence_refs:
support_status:
qa_status:
```

## Support statuses

- SUPPORTED;
- SUPPORTED_WITH_QUALIFICATION;
- USER_ATTESTED;
- ASSUMPTION;
- UNSUPPORTED;
- CONFLICTED;
- STALE.

## Drafting rule

The drafting worker may write an assumption only if clearly represented as future plan/assumption rather than historical fact.

## Tests

- synthetic testimonial fails support;
- future target not misclassified as achieved outcome;
- numerical claim traces to statistic/budget/fact;
- humanization cannot sever claim ledger mapping silently.

---

# 21. Chapter B5.C17 — Research Finding Model

## Objective

Turn funder/winner/community research into durable evidence-backed objects rather than disposable prose.

## ResearchFinding

```yaml
finding_id:
research_type:
subject_refs:
statement:
evidence_refs:
quality:
applicability:
limitations:
created_at:
created_by:
```

Research types:

- FUNDER_PRIORITY;
- HISTORICAL_WINNER_PATTERN;
- AWARD_RANGE;
- GEOGRAPHIC_PATTERN;
- PROGRAM_ALIGNMENT;
- COMMUNITY_NEED;
- COMPETITIVE_SIGNAL;
- REQUIREMENT_INTERPRETATION;
- OTHER.

## Causal caution

Historical winner patterns are descriptive unless evidence supports stronger inference. The system must not say “winners always do X” from a weak sample.

## Tests

- finding requires evidence;
- limitation preserved;
- award sample size represented;
- research finding can be shown to client and consumed by drafting context.

---

# 22. Chapter B5.C18 — Audit ↔ Evidence ↔ Decision Linkage

## Objective

Unify Book 1 audit events with Book 5 decision/evidence records.

## Required linkage

A consequential action should allow traversal:

```text
AuditEvent
→ PolicyDecision
→ Capability
→ DecisionRecord / Operation
→ Evidence inputs
→ Output artifacts
→ Human approval if any
```

And reverse traversal:

```text
Proposal artifact
→ generating decision/task
→ evidence
→ actor
→ policy decision
→ audit event
```

## Tests

- orphaned consequential decision rejected;
- approval reference resolves;
- actor/capability consistent between audit and decision;
- sensitive payload redaction does not destroy lineage.

## Commit

`G0-B5-C14-C18: ratify substrate decision and client/audit evidence contracts`

---

# 23. Chapter B5.C19 — Evaluation Dataset Lineage

## Objective

Prepare Book 7 so eval cases are trustworthy and reproducible.

## EvalCaseLineage

Each benchmark/eval example derived from system work must record:

```text
case ID
source snapshot refs
domain fixture refs
decision/artifact refs
label origin
label reviewer
created_at
applicable version/time
privacy classification
split membership
```

## Rules

- training/eval leakage detectable;
- changed source does not mutate historical eval case silently;
- human labels distinguished from model-generated labels;
- synthetic cases labeled synthetic;
- tenant-private cases require explicit governance before use in generalized evaluation/training.

## Tests

- eval case without lineage rejected;
- label provenance required;
- historical benchmark reproducible;
- private tenant data not exported into global eval by default.

---

# 24. Chapter B5.C20 — D0/D1 Evidence Readiness

## Objective

Strengthen the early drafting milestones with inspectable evidence.

## D0 Shadow Draft requirements

The Book 3 D0 mock should now produce:

```text
Mock Proposal ArtifactVersion
+
Application Claim Ledger
+
Research Findings
+
Evidence graph/provenance refs
+
QA factuality result
+
ExplanationPacket
```

## D1 Hermes Draft requirements

CEO Hermes must receive evidence through a bounded ContextBundle, not unrestricted graph/database access.

Worker receives only evidence relevant to assigned requirements/sections.

WorkerResult returns:

- draft content/artifact ref;
- claims created;
- evidence used;
- assumptions;
- unresolved evidence gaps;
- sidechain ref.

## Gate

A mock can be stylistically complete while still labeled `EVIDENCE_INCOMPLETE`. It cannot be falsely marked submission-ready.

## Tests

- D0 claim ledger coverage threshold measured;
- D1 context excludes unrelated tenant/project evidence;
- Personal Hermes explanation reflects CEO decision packet;
- missing evidence surfaces as gap rather than hallucinated support.

---

# 25. Chapter B5.C21 — Performance & Scale Envelope

## Objective

Prevent a theoretically elegant evidence graph from becoming operationally unusable.

## Benchmark fixture sizes

At minimum test:

- 1 tenant / 10 opportunities;
- 10 tenants / 1k opportunities;
- synthetic scale: 100 tenants / 100k opportunities / millions of evidence edges where practical for prototype benchmarking.

Exact scale can be adjusted to local resources, but test methodology and extrapolation must be explicit.

## Workloads

- exact provenance trace;
- contradiction lookup;
- dependency invalidation;
- application evidence bundle assembly;
- historical replay packet assembly;
- graph traversal;
- vector retrieval if enabled.

## Metrics

- p50/p95 latency;
- memory;
- storage growth;
- rebuild time;
- projection lag;
- invalidation fanout;
- failure behavior.

## Rule

No arbitrary enterprise SLA invented in G0. Establish measured baseline and G1 target recommendations.

---

# 26. Chapter B5.C22 — Privacy, Retention & Evidence Visibility

## Objective

Ensure evidence architecture respects client/private data boundaries.

## Visibility classes

- PUBLIC_SOURCE;
- TENANT_PRIVATE;
- TENANT_SHARED_APPROVED;
- PLATFORM_INTERNAL;
- RESTRICTED_SENSITIVE.

## Rules

- public source evidence may be reused subject to source/license policy;
- tenant-private evidence is not globally retrievable;
- graph edges inherit/compute visibility safely;
- derived embeddings respect source visibility;
- deletion/retention policy can restrict current access while preserving legally/operationally required audit tombstones/hashes;
- explanation packets filter evidence by viewer authority.

## Tests

- public+private mixed graph query does not leak private node metadata;
- vector index honors deletion;
- evidence visibility survives projection/rebuild;
- tenant export can enumerate its own evidence lineage.

---

# 27. Chapter B5.C23 — Failure & Degraded Modes

## Objective

Define behavior when optional evidence infrastructure fails.

## Scenarios

### Graph projection unavailable

Core canonical state/decision recording continues where relational substrate permits. Graph-enhanced traversal degrades.

### Vector store unavailable

Exact/relational/full-text retrieval continues; semantic retrieval disabled.

### Semantica unavailable

If adopted as optional projection/accelerator, system continues without losing canonical state.

### Provenance write failure

Material decision/output requiring provenance must fail closed rather than create untraceable production state.

### Historical evidence missing/corrupt

Replay marked integrity failure; do not fabricate reconstruction.

### Contradiction service unavailable

Do not auto-promote conflicted facts.

## Tests

Every optional component has explicit degraded behavior; every integrity-critical component has fail-closed behavior.

---

# 28. Chapter B5.C24 — Adversarial Evidence Test Suite

## Objective

Attack evidence integrity before Book 6/7/8 rely on it.

Required scenarios:

1. proposal claim points to source that never contained it;
2. locator points to wrong PDF page;
3. model cites secondary source while decision used official source;
4. generated research summary recursively cited as evidence;
5. two “independent” corroborations are copies of same upstream article;
6. stale high-authority source vs current official amendment;
7. current source incorrectly substituted into historical replay;
8. graph node created without canonical entity;
9. graph mutation attempts to create canonical fact;
10. vector top result conflicts with canonical fact;
11. cross-tenant nearest-neighbor leak;
12. evidence edge crosses tenants;
13. deleted private evidence remains retrievable through embedding;
14. contradiction resolution deletes losing claim;
15. model confidence resolves hard official conflict;
16. opportunity revision changes but old eligibility remains current;
17. community statistic geography mismatch;
18. statistic unit mismatch;
19. award recipient entity resolution wrong;
20. proposal historical outcome is actually future target;
21. synthetic testimonial presented as verified;
22. budget number has no derivation lineage;
23. humanization changes supported number after QA;
24. Semantica unavailable during draft generation;
25. Semantica state deleted and rebuild attempted;
26. graph projection lag serves stale dependency result;
27. evidence hash mismatch;
28. audit event and decision actor disagree;
29. eval case label has no reviewer/source lineage;
30. tenant-private case enters global eval without approval;
31. malicious source content attempts to create SUPPORTS edge to itself;
32. source duplicate masquerades as corroboration;
33. evidence quality composite hides stale dimension;
34. missing historical model metadata;
35. unsupported causal conclusion from winner research;
36. old resolved contradiction becomes relevant after new amendment;
37. dependency cycle causes invalidation storm;
38. evidence graph query returns unauthorized restricted metadata;
39. source/license restriction conflicts with retention/reuse;
40. explanation packet omits known material uncertainty.

All P0 integrity/security scenarios must pass.

---

# 29. Chapter B5.C25 — Integration & Property Tests

## Mandatory invariants

```text
1. Every material operational claim is evidence-linked or explicitly qualified.
2. Generated text cannot self-authorize as evidence.
3. SourceSnapshot lineage survives normalization.
4. Claim promotion is explicit.
5. Contradictory evidence is retained.
6. Decisions pin exact input revisions.
7. Historical replay never substitutes current state silently.
8. Dependency invalidation is selective and traceable.
9. Retrieval rank is not authority.
10. Vector indexes are disposable/rebuildable.
11. Graph projections are disposable/rebuildable.
12. Internal canonical IDs survive all projections.
13. Cross-tenant graph/vector access is denied.
14. Explanation packets match decision evidence.
15. Claim ledger survives drafting/QA/humanization transformations.
16. Research findings preserve evidence and limitations.
17. Audit events link to decisions/evidence/output.
18. Eval cases retain lineage.
19. Optional Semantica failure does not destroy canonical operation.
20. Provenance-integrity failure blocks consequential promotion/finalization.
```

## Property tests

Where practical:

- graph projection rebuild produces semantic-equivalent node/edge set;
- vector index rebuild resolves to same canonical refs, allowing ranking variance;
- deterministic derived facts replay exactly;
- append-only contradiction history remains immutable;
- dependency invalidation is idempotent;
- serialization round-trip preserves DecisionRecord semantics.

---

# 30. Chapter B5.C26 — Book 5 Reality Lock

## Machine-readable result

```json
{
  "book": "G0-B5",
  "status": "PASS|FAIL",
  "evidence_constitution_complete": true,
  "provenance_model_pass": true,
  "evidence_graph_semantics_pass": true,
  "decision_record_pass": true,
  "historical_replay_pass": true,
  "contradiction_retention_pass": true,
  "dependency_invalidation_pass": true,
  "retrieval_authority_pass": true,
  "graph_rebuild_exit_pass": true,
  "vector_rebuild_exit_pass": true,
  "semantica_bakeoff_complete": true,
  "storage_adr_ratified": true,
  "tenant_isolation_pass": true,
  "claim_ledger_pass": true,
  "client_explanation_pass": true,
  "audit_evidence_linkage_pass": true,
  "eval_lineage_pass": true,
  "d0_d1_evidence_ready": true,
  "adversarial_p0_pass": true,
  "p0_open": 0,
  "ready_for_book6": true
}
```

No `ready_for_book6=true` if the storage decision is still “TBD” or if an adopted optional framework cannot pass its exit/rebuild test.

---

# 31. Chapter B5.C27 — Precise Handoff to Book 6

Book 6 receives:

```text
ProvenanceRef contract
Evidence graph edge semantics
Evidence visibility classes
DecisionRecord contract
Audit↔decision↔evidence linkage
Tenant-scoped retrieval requirements
Graph/vector projection boundaries
Storage ADR
Optional framework role
Failure/degraded modes
Human approval lineage requirements
```

Book 6 then answers:

> Which authenticated identity may retrieve, mutate, approve, export or act on these resources, through which capability/tool gateway, with which secret and tenant boundaries?

Book 6 must not redefine evidence authority merely because an integration exposes a convenient API.

---

# 32. Parallel-Agent Work Allocation

## Lane A — Evidence Core

Owns C1–C6:

- constitution;
- provenance;
- graph semantics;
- quality;
- promotion;
- contradiction.

Lands first.

## Lane B — Decision & Replay

After core refs stabilize:

- C7 DecisionRecord;
- C8 replay;
- C9 dependency invalidation.

## Lane C — Retrieval & Projection

- C10 retrieval;
- C11 vector;
- C12 graph projection.

## Lane D — Semantica Bake-Off

- C13 workloads/implementation;
- results;
- C14 storage ADR.

Cannot ratify storage ADR before Lane A/C contracts stabilize.

## Lane E — Product Evidence

- C15 explanation;
- C16 claim ledger;
- C17 research findings;
- C18 audit linkage;
- C20 D0/D1 readiness.

## Lane F — Evaluation/Security/Scale

- C19 eval lineage;
- C21 performance;
- C22 privacy;
- C23 degradation;
- C24/C25 tests.

## Merge law

No lane may create a second evidence authority model or let a chosen framework redefine Book 2/3 identities.

---

# 33. Commit Plan

```text
1.  G0-B5-C1
    evidence constitution

2.  G0-B5-C2-C3
    provenance + graph semantics

3.  G0-B5-C4-C6
    quality + promotion + contradiction

4.  G0-B5-C7-C9
    decisions + replay + invalidation

5.  G0-B5-C10-C12
    retrieval + vector + graph projection

6.  G0-B5-C13
    Semantica bake-off implementation/results

7.  G0-B5-C14
    storage decision ADR

8.  G0-B5-C15-C18
    explanation + claim ledger + research + audit linkage

9.  G0-B5-C19-C20
    eval lineage + D0/D1 readiness

10. G0-B5-C21-C23
    performance + privacy + degradation

11. G0-B5-C24-C25
    adversarial + integration/property tests

12. G0-B5-BOOK
    complete Book 5 evidence packet

13. G0-B5-REPAIR-1...N
    review repairs

14. G0-B5-RATIFY
    Reality Lock PASS
```

The agent should continue without chapter-by-chapter approval unless it encounters a P0 constitutional contradiction, licensing blocker, irreconcilable storage constraint, or evidence showing a previously frozen assumption is false.

---

# 34. Allowed / Prohibited Paths

## Allowed

- Book 5 docs;
- evidence/provenance schemas/config;
- disposable evidence substrate prototypes;
- Semantica adapter/bake-off code;
- graph/vector projection prototypes;
- tests/fixtures/benchmarks;
- ADR/evidence packets.

## Prohibited

- changing Book 2 ontology sovereignty;
- changing Book 3 source authority semantics without amendment;
- making Semantica canonical by convenience;
- production external submission;
- storing secrets in graph/vector metadata;
- using tenant-private evidence globally without governance;
- production self-modification;
- unrelated trading/OCE implementation.

---

# 35. Definition of Done

Book 5 is complete only when:

1. evidence constitutional laws are ratified;
2. provenance refs resolve across core domain objects;
3. graph semantics are technology-independent;
4. evidence quality dimensions are inspectable;
5. promotion/contradiction history is explicit and append-preserving;
6. material decisions have version-pinned DecisionRecords;
7. historical replay works;
8. selective dependency invalidation works;
9. retrieval cannot override authority;
10. vector/graph indexes are rebuildable;
11. Semantica has been empirically tested, not merely discussed;
12. physical storage ADR is ratified;
13. client ExplanationPacket works without chain-of-thought;
14. application claim ledger traces material draft claims;
15. research findings retain evidence/limitations;
16. audit↔decision↔evidence traversal works;
17. eval cases have lineage;
18. D0/D1 drafting evidence contracts are ready;
19. privacy/tenant isolation passes across graph/vector/retrieval;
20. optional component failures degrade safely;
21. adversarial P0 tests pass;
22. Reality Lock reports zero open P0 and `ready_for_book6=true`.

---

# 36. Book 5 North-Star Test

Take one sentence from a generated Georgia grant proposal—for example a factual statement about the applicant, a community need statistic, an opportunity deadline, a historical award pattern or a budget amount.

The system should be able to answer, without hidden agent memory:

```text
Where did this claim come from?
Which exact source revision supported it?
What evidence quality did it have?
Was anything contradictory known?
Who/what promoted or accepted the fact?
Which decision used it?
Which proposal version contains it?
What happens if the source changes tomorrow?
Can we reconstruct what the system knew when it wrote the sentence?
Can the client see a useful explanation of that support?
Can we replace the graph/RAG framework and still answer all of the above?
```

If any of those answers depend on “the agent probably remembers,” Book 5 fails.