# G0 Book 4 — Dual-Hermes Protocol & Memory Constitution Master Implementation Plan

**Document ID:** GS-G0-B4-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR CONTINUOUS EXECUTION AFTER BOOK 3 RATIFICATION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Parent plan:** `G0_FULL_MASTER_BUILD_BLUEPRINT_v1.0.md`  
**Receives from:** Book 1 Product Constitution, Book 2 Domain Ontology, Book 3 Grant Intelligence Data Constitution  
**Hands off to:** Book 5 Evidence/Provenance Substrate, Book 6 Security/Tool Authority, Book 7 Evaluation, and the D1 Hermes Mock-Draft Milestone

---

# 0. Book Mission

Book 4 defines the **cognitive operating protocol of the product**.

Books 1–3 establish:

- who is allowed to act;
- what all grant-domain objects mean;
- how external reality becomes governed data.

Book 4 now answers:

> How do the client, Personal Hermes, CEO Hermes, specialist workers, deterministic services, and durable system state communicate without collapsing into one polluted context window or one unbounded memory system?

This book is intentionally designed around the project’s central architectural insight:

> **Relationship intelligence and operational intelligence are different jobs and must remain separate.**

Personal Hermes should become increasingly good at understanding the client.

CEO Hermes should become increasingly good at operating the product.

Workers should become good at one bounded task and then disappear.

Canonical truth should remain outside all three.

The result must preserve client continuity without creating infinite memory, preserve worker depth without polluting parent context, and allow the entire agent layer to be restarted/replaced without destroying business state.

---

# 1. Book Theme

## Relationship → Intent → Authority → Plan → Bounded Work → Result → Synthesis → Explanation → Selective Memory

Canonical flow:

```text
CLIENT
  ↓
PERSONAL HERMES
  ↓
IntentContract
  ↓
CONTROL / POLICY
  ↓
CEO HERMES
  ↓
TaskPlan
  ↓
TaskContracts
  ↓
SPECIALIST WORKERS / DETERMINISTIC SERVICES
  ↓
WorkerResults + sidechains
  ↓
CEO Synthesis
  ↓
OutcomeArtifact
  ↓
PERSONAL HERMES
  ↓
ClientExplanationPacket
  ↓
CLIENT
```

Memory is not a second hidden pathway around this protocol.

---

# 2. Hard Inputs from Books 1–3

Book 4 receives these invariants as non-negotiable unless an amendment is raised:

1. Personal Hermes and CEO Hermes are separate actors.
2. Personal Hermes initial authority ceiling = L1.
3. CEO Hermes initial authority ceiling = L2.
4. workers receive task-scoped L0/L2 authority only.
5. agent memory is not canonical system truth.
6. drafting/research are allowed at L2.
7. submission/signing/certification remain disabled.
8. tenant/project scope is mandatory.
9. external facts require Book 3 provenance.
10. eligibility and other deterministic constraints remain deterministic.
11. `ApplicationProject`, `OpportunityRevision`, `EvidenceClaim`, `CanonicalFact`, `StatisticObservation`, `Artifact`, etc. retain Book 2 meanings.
12. source revisions create new state rather than silently rewriting old facts.
13. worker traces must not automatically enter Personal/CEO active context.
14. raw secrets cannot enter memory/prompts/sidechains/logs.
15. client-visible material research is a product requirement.
16. proposal and business plan remain distinct artifacts.
17. Georgia-first D0/D1 testing remains the initial state proof priority.

---

# 3. Book 4 Build Philosophy

## 3.1 Protocol before personality

Do not rely on “good prompting” to preserve separation between Hermes roles. Their interaction must be governed by typed contracts.

## 3.2 Memory should reduce future work, not preserve every token

Retain stable facts, decisions, preferences, goals, active loops and validated lessons. Archive or expire execution chatter.

## 3.3 Memory is role-specific

Personal memory answers:

> What should I remember to understand and help this client?

CEO memory answers:

> What should I retain to operate this product efficiently and correctly?

Worker memory answers:

> What is necessary to complete this task?

Usually nothing survives after the task except a result, trace and promoted lesson.

## 3.4 Context is assembled, not accumulated

Each operation receives a **ContextBundle** assembled from canonical state and selected memory rather than inheriting an ever-growing conversation transcript.

## 3.5 Sidechains preserve depth without parent pollution

Full worker execution remains inspectable, but parent Hermes receives a bounded structured result plus trace pointer.

## 3.6 Compression must preserve anchors

Important decisions, active constraints, unresolved questions, current application state and source revision references cannot be accidentally summarized away.

## 3.7 Forgetting is intentional

Expired/stale execution detail should disappear from active memory unless promoted.

## 3.8 Learning is not memory accumulation

A repeated pattern becomes a candidate lesson, then must pass Book 7/evaluation governance before becoming durable operational doctrine.

## 3.9 The client must experience one coherent assistant

The internal separation should improve quality without making the user feel forced to manually coordinate multiple agents.

Personal Hermes remains the primary conversational surface unless product UX intentionally exposes CEO/system detail.

---

# 4. Required Book 4 Artifact Set

```text
docs/grant-sector/g0/04-dual-hermes/
├── G0_B4_DUAL_HERMES_CONSTITUTION.md
├── G0_B4_PERSONAL_HERMES_CONTRACT.md
├── G0_B4_CEO_HERMES_CONTRACT.md
├── G0_B4_WORKER_CONTRACT.md
├── G0_B4_FEED_FORWARD_PROTOCOL.md
├── G0_B4_INTENT_PROTOCOL.md
├── G0_B4_TASK_DELEGATION_PROTOCOL.md
├── G0_B4_RESULT_SYNTHESIS_PROTOCOL.md
├── G0_B4_CONTEXT_ASSEMBLY_POLICY.md
├── G0_B4_PERSONAL_MEMORY_CONSTITUTION.md
├── G0_B4_CEO_MEMORY_CONSTITUTION.md
├── G0_B4_WORKER_MEMORY_POLICY.md
├── G0_B4_MEMORY_PROMOTION_POLICY.md
├── G0_B4_MEMORY_SUPERSESSION_POLICY.md
├── G0_B4_CONTEXT_COMPACTION_POLICY.md
├── G0_B4_SIDECHAIN_TRACE_POLICY.md
├── G0_B4_RECONSTRUCTION_PROTOCOL.md
├── G0_B4_CLARIFICATION_ESCALATION_PROTOCOL.md
├── G0_B4_D1_HERMES_DRAFT_CONTRACT.md
├── G0_B4_ADR_REGISTER.md
├── G0_B4_TEST_REPORT.md
├── G0_B4_ADVERSARIAL_TEST_REPORT.md
├── G0_B4_REALITY_LOCK_REPORT.md
└── G0_B4_HANDOFF_TO_BOOK_5.md

schemas/g0/agents/
├── intent_contract.schema.json
├── clarification_request.schema.json
├── task_plan.schema.json
├── task_contract.schema.json
├── worker_result.schema.json
├── outcome_artifact.schema.json
├── client_explanation_packet.schema.json
├── context_bundle.schema.json
├── memory_candidate.schema.json
├── memory_record.schema.json
├── memory_promotion.schema.json
├── memory_supersession.schema.json
├── sidechain_manifest.schema.json
└── reconstruction_manifest.schema.json

config/g0/agents/
├── personal_memory_classes.yaml
├── ceo_memory_classes.yaml
├── worker_context_policy.yaml
├── context_budget_policy.yaml
├── compaction_policy.yaml
├── memory_ttl_policy.yaml
└── clarification_policy.yaml

prototype/g0/agents/
├── intent_builder.py
├── context_builder.py
├── task_builder.py
├── result_reducer.py
├── memory_manager.py
├── compactor.py
├── reconstruction.py
└── fixtures/

tests/g0/book4/
├── test_intent_contract.py
├── test_context_boundaries.py
├── test_task_delegation.py
├── test_worker_sidechains.py
├── test_personal_memory.py
├── test_ceo_memory.py
├── test_memory_promotion.py
├── test_memory_supersession.py
├── test_compaction.py
├── test_reconstruction.py
├── test_clarification_flow.py
├── test_d1_mock_draft_flow.py
└── test_adversarial_context_pollution.py
```

---

# 5. Chapter B4.C1 — Dual-Hermes Constitutional Boundary

## Objective

Freeze why two Hermes instances exist and what problem each solves.

## Personal Hermes

Optimization objective:

> Maximize client understanding, continuity, clarity and usable intent formation while minimizing unnecessary operational context.

## CEO Hermes

Optimization objective:

> Maximize reliable execution, workflow coherence, bounded delegation and operational learning while minimizing irrelevant relationship/chat history.

## Shared constraints

Both:

- obey Book 1 authority;
- use Book 2 domain semantics;
- consume Book 3 governed facts/evidence;
- do not become canonical truth;
- never store secrets;
- cannot silently expand own authority;
- can be reset/replaced.

## Anti-collapse rule

The system must not “temporarily” combine Personal + CEO memory into one permanent namespace merely for implementation convenience.

## Deliverables

- dual-Hermes rationale;
- role boundary matrix;
- prohibited overlap table;
- handoff responsibilities.

## Tests

- no capability requires Personal Hermes to perform CEO execution;
- no CEO workflow requires full raw client chat history;
- no shared mutable memory store is the only source for either role.

## Commit

`G0-B4-C1: freeze dual-Hermes cognitive boundary`

---

# 6. Chapter B4.C2 — Personal Hermes Operating Contract

## Objective

Define Personal Hermes as a first-class product interface rather than generic chat wrapper.

## Responsibilities

- conversational intake;
- brainstorming;
- idea development;
- clarification;
- capture of client preferences;
- identification of client goals/open loops;
- explanation of system outcomes;
- proposed corrections to organization/profile information;
- translation of user intent to `IntentContract`;
- request/answer handling between client and CEO.

## Explicit non-responsibilities

Personal Hermes does not:

- run broad grant research directly unless through an approved bounded capability;
- directly mutate canonical system state;
- manage worker fleets;
- hold external credentials;
- submit applications;
- accept its own conversational inference as canonical organization truth;
- store every conversation verbatim in active memory.

## Required context classes

Personal Hermes may receive:

- current user message;
- curated relationship memory;
- relevant canonical organization facts;
- selected active goals/open loops;
- latest outcome/explanation packet;
- limited application/project summaries;
- clarification requests from CEO.

## Output classes

- conversational response;
- IntentContract;
- ClarificationAnswer;
- MemoryCandidate;
- CanonicalFact update proposal;
- client feedback/correction event.

## Tests

- Personal Hermes cannot call `application.submit`;
- client casually mentioning changed revenue creates a fact proposal/candidate, not silent canonical mutation;
- old unrelated grant-work transcript excluded from a new brainstorming context unless relevant.

---

# 7. Chapter B4.C3 — CEO Hermes Operating Contract

## Objective

Define CEO Hermes as a governed application operator, not a second general-purpose chat companion.

## Responsibilities

- interpret approved IntentContracts;
- inspect canonical application/system state;
- create TaskPlans;
- issue TaskContracts;
- select specialist/deterministic capabilities;
- supervise bounded work;
- monitor retries/blockers;
- synthesize results;
- produce OutcomeArtifacts;
- propose workflow improvements;
- maintain lean operational continuity;
- request clarification when intent/data is insufficient.

## Explicit non-responsibilities

CEO Hermes does not:

- act as canonical database;
- hold full user conversation history by default;
- hold raw secrets;
- self-authorize L3/L4/L5 expansion;
- submit applications in current phase;
- maintain permanent raw worker transcripts;
- silently promote worker findings to canonical facts;
- invent missing eligibility evidence.

## CEO context classes

- IntentContract;
- application/project summary;
- relevant Book 2 domain objects;
- Book 3 verified/evidence data;
- active operational memory;
- current TaskPlan/task statuses;
- promoted operational lessons;
- policy/capability summary;
- failure/health signals.

## Tests

- CEO can operate with no raw Personal transcript given a complete IntentContract;
- CEO requests clarification rather than guessing an unresolved critical constraint;
- CEO context excludes closed project chatter after archival unless explicitly retrieved.

## Commit

`G0-B4-C2-C3: define Personal and CEO Hermes operating contracts`

---

# 8. Chapter B4.C4 — IntentContract

## Objective

Define the central boundary translating human conversation into operational work.

## IntentContract schema

```yaml
intent_id:
tenant_id:
client_actor_id:
organization_id:
intent_type:
objective:
desired_outcome:
constraints:
known_facts_refs:
user_assertions:
open_questions:
non_goals:
priority:
deadline_or_time_horizon:
authority_scope:
requested_capabilities:
confidence_state:
source_conversation_refs:
created_at:
```

## Example

```text
User:
"I want to see if we can get funding for an after-school program for working parents around here."

Personal Hermes may clarify:
- age group?
- geography?
- current organization/program status?
- pilot or permanent program?

Then emit:
IntentType = EXPLORE_PROGRAM_FUNDING
Objective = identify and assess funding for after-school youth program
Geography = Atlanta/Georgia
Authority = RESEARCH_AND_DRAFT_ONLY
OpenQuestions = unresolved budget/facility constraints
```

## Intent classes

Initial:

- EXPLORE_IDEA;
- FIND_GRANTS;
- ASSESS_OPPORTUNITY;
- BUILD_APPLICATION;
- UPDATE_PROFILE;
- REVIEW_DRAFT;
- RESEARCH_FUNDER;
- RESEARCH_WINNERS;
- EXPLAIN_RESULT;
- OTHER_CONTROLLED_EXTENSION.

## Hard rules

- raw conversation is linked, not embedded wholesale;
- known canonical facts use refs;
- user assertions are labeled as assertions until promoted;
- authority scope explicit;
- unresolved critical questions remain visible.

## Tests

- intent missing tenant fails;
- intent requesting submission while phase disabled is rejected/normalized to prepare-only;
- user assertion does not become canonical fact;
- conversation reference remains retrievable for audit without entering CEO active context.

---

# 9. Chapter B4.C5 — Clarification Protocol

## Objective

Allow CEO to obtain missing information without becoming a second independent client relationship.

## ClarificationRequest

```yaml
clarification_id:
intent_id:
requesting_actor:
question_type:
question:
why_needed:
blocking:
expected_answer_type:
allowed_context_refs:
created_at:
```

## Flow

```text
CEO identifies missing critical input
        ↓
ClarificationRequest
        ↓
Personal Hermes
        ↓
asks user naturally
        ↓
ClarificationAnswer
        ↓
Intent amendment / fact proposal
        ↓
CEO resumes
```

## Rules

- CEO should not repeatedly ask questions Personal memory/canonical state can answer;
- Personal should not answer on behalf of client when only inference exists;
- blocking vs non-blocking clarification is explicit;
- context of why CEO needs answer may be translated into user-friendly language.

## Tests

- no duplicate clarification when answer already canonical;
- unresolved eligibility-critical question blocks eligible status/draft readiness appropriately;
- clarification answer updates IntentContract version rather than mutating prior intent history silently.

## Commit

`G0-B4-C4-C5: freeze intent and clarification protocol`

---

# 10. Chapter B4.C6 — TaskPlan

## Objective

Define CEO’s operational decomposition before work is delegated.

## TaskPlan

```yaml
plan_id:
intent_id:
application_project_id:
objective:
steps:
dependencies:
parallelizable_groups:
critical_path:
required_capabilities:
budget_constraints:
time_constraints:
stop_conditions:
human_review_points:
created_by:
version:
```

## Plan principles

- explicit dependency graph;
- deterministic services used where available;
- worker count should reflect work, not agent theater;
- parallel work only when context/data boundaries allow;
- plan is versioned when material assumptions change.

## Example grant application plan

```text
1. Verify opportunity revision
2. Evaluate eligibility
3. Research funder
4. Research prior winners
5. Gather community evidence
6. Normalize requirements
7. Build application blueprint
8. Draft sections in bounded clusters
9. Reconcile budget
10. Cross-document QA
11. Client review packet
```

Steps 3–5 may run in parallel after 1–2 pass.

## Tests

- plan cannot schedule drafting before a required hard-eligibility failure is resolved unless explicitly mock/research-only;
- circular dependencies rejected;
- plan requiring disabled capability rejected.

---

# 11. Chapter B4.C7 — TaskContract

## Objective

Create a minimum-information, maximum-clarity worker boundary.

## TaskContract

```yaml
task_id:
plan_id:
tenant_id:
project_id:
worker_role:
objective:
capability_id:
inputs_refs:
allowed_context_refs:
constraints:
required_outputs:
quality_gates:
source_requirements:
authority_scope:
side_effect_policy:
max_attempts:
time_budget:
token_or_cost_budget:
expires_at:
```

## Context minimization rule

Workers receive object/evidence refs or bounded extracted context—not the full CEO prompt/history.

## Worker examples

- FunderResearchWorker;
- WinnerResearchWorker;
- CommunityEvidenceWorker;
- RequirementNormalizationWorker;
- ProposalSectionWorker;
- BusinessPlanWorker;
- BudgetValidationWorker;
- CitationQAWorker.

These are logical roles, not necessarily permanent processes/models.

## Tests

- task cannot omit tenant/project scope;
- task cannot grant capability above CEO’s delegated authority;
- worker cannot access unlisted context ref;
- task expiration enforced;
- retries retain same task lineage/new attempt ID.

## Commit

`G0-B4-C6-C7: define CEO planning and task delegation contracts`

---

# 12. Chapter B4.C8 — Worker Execution & Sidechain Protocol

## Objective

Preserve full forensic depth without contaminating CEO active context.

## Sidechain model

Each worker attempt produces:

```text
SidechainManifest
- task_id
- attempt_id
- worker identity/model/provider
- start/end time
- tool/capability calls
- source/artifact refs
- errors/retries
- full transcript/object URI
- token/cost metrics
- redaction status
- retention class
```

## WorkerResult

Parent-facing bounded result:

```yaml
task_id:
attempt_id:
status:
summary:
structured_output_ref:
key_findings:
uncertainties:
source_refs:
artifact_refs:
quality_state:
recommended_followups:
sidechain_ref:
```

## Rules

- CEO receives WorkerResult by default, not transcript;
- transcript available for debugging/review via explicit retrieval;
- sidechain cannot contain raw secrets;
- high-value evidence is promoted to Book 3 objects, not trapped in transcript;
- failed attempt remains part of audit lineage.

## Tests

- 50k-token worker trace returns bounded parent payload;
- CEO can retrieve exact source/artifact refs without transcript injection;
- secret fixture redacted/rejected;
- failed/retried attempts maintain unique attempt IDs and shared task lineage.

---

# 13. Chapter B4.C9 — WorkerResult Reduction & CEO Synthesis

## Objective

Define how multiple bounded worker outputs become one coherent operational result.

## Result reduction

CEO should synthesize from:

- structured outputs;
- promoted/verified evidence;
- task quality state;
- unresolved conflicts;
- deterministic results;
- application state.

Not simply concatenate summaries.

## OutcomeArtifact

```yaml
outcome_id:
intent_id:
plan_id:
application_project_id:
outcome_type:
status:
executive_summary:
key_decisions:
recommended_actions:
research_pack_refs:
artifact_refs:
unresolved_questions:
risks:
qa_refs:
source/evidence_refs:
client_action_required:
created_at:
```

## Rules

- uncertainty preserved;
- contradictory worker outputs surfaced/resolved through evidence, not majority vote by default;
- outcome links to canonical state/artifacts instead of duplicating entire documents;
- client-action-required explicitly marked.

## Tests

- two conflicting worker results do not silently average into false consensus;
- failed critical task prevents success status;
- outcome points to exact application/opportunity revision.

## Commit

`G0-B4-C8-C9: freeze sidechain, worker-result and CEO synthesis protocol`

---

# 14. Chapter B4.C10 — ClientExplanationPacket

## Objective

Separate operational synthesis from the way results are communicated to the client.

## ClientExplanationPacket

```yaml
explanation_id:
outcome_id:
audience:
summary:
what_we_found:
why_it_matters:
recommended_next_step:
questions_for_client:
visible_research_refs:
visible_artifact_refs:
uncertainty_disclosures:
```

## Personal Hermes role

Personal Hermes may:

- adapt language to user preference;
- explain technical status;
- connect result to prior goals;
- ask follow-ups;
- surface research visually.

Personal Hermes may not:

- alter underlying factual conclusions;
- hide material uncertainty;
- change dollar amounts/deadlines;
- represent mock as submitted/final.

## Tests

- explanation preserves core outcome facts;
- visible past-winner/funder research requirement satisfied;
- style transformation cannot change factual fixture values.

---

# 15. Chapter B4.C11 — ContextBundle Architecture

## Objective

Replace “send the whole conversation” with explicit contextual assembly.

## ContextBundle

```yaml
context_bundle_id:
consumer_actor:
operation_type:
tenant_id:
project_id:
canonical_state_refs:
evidence_refs:
memory_refs:
recent_interaction_refs:
policy_refs:
task_refs:
anchors:
excluded_context_classes:
context_budget:
assembled_at:
```

## Context assembly order

```text
1. required canonical state
2. required current evidence
3. active task/project state
4. mandatory policy/constraints
5. promoted role-specific memory
6. selected recent interaction context
7. optional supporting history within budget
```

## Never default-inject

- entire user history;
- entire worker traces;
- closed project transcripts;
- secrets;
- irrelevant application documents;
- stale memory marked superseded.

## Context budget

Budget measured in:

- tokens/characters;
- item count;
- relevance class;
- mandatory vs optional priority.

## Tests

- mandatory anchors survive budget pressure;
- irrelevant old conversations excluded;
- same operation produces deterministic mandatory context refs given same state.

## Commit

`G0-B4-C10-C11: define client explanation and context assembly contracts`

---

# 16. Chapter B4.C12 — Personal Memory Constitution

## Objective

Define persistent relationship continuity without infinite autobiographical storage.

## Personal durable memory classes

### PM-IDENTITY

Stable client/organization relationship context that is not otherwise better represented as canonical domain facts.

### PM-PREFERENCE

Communication/work preferences.

Examples:

- prefers concise explanations;
- wants opportunities prioritized by deadline/fit;
- wants drafts surfaced before full package.

Preferences are not business facts.

### PM-GOAL

Longer-lived user objectives.

### PM-DECISION

Meaningful user choices/commitments not yet fully represented in domain state.

### PM-RELATIONSHIP

Relevant partner/funder/contact context, subject to privacy/data policy.

### PM-OPEN_LOOP

Unresolved ideas/questions the user expects to revisit.

### PM-EPISODIC_SUMMARY

Compressed meaningful interaction episode.

## Do not store as Personal memory when canonical domain state is superior

Examples:

- EIN;
- grant deadline;
- award ceiling;
- verified revenue;
- application status;
- source-backed statistic.

Store a reference to canonical state instead.

## Memory record fields

```yaml
memory_id:
memory_class:
tenant/user scope:
statement:
source_event_refs:
created_at:
last_confirmed_at:
importance:
confidence_state:
expires_at:
supersedes:
canonical_refs:
privacy_class:
```

## Tests

- stable preference survives conversation compaction;
- official grant deadline is not duplicated as freeform personal memory truth;
- old preference can be superseded;
- user correction produces new record/supersession.

---

# 17. Chapter B4.C13 — CEO Memory Constitution

## Objective

Define lean operational continuity.

## CEO durable memory classes

### CM-SYSTEM-DOCTRINE

References ratified laws/contracts, ideally by version rather than copied prose.

### CM-ACTIVE-PROJECT

Operational summary of active project/application state.

### CM-BLOCKER

Known unresolved failure/blocker requiring continued attention.

### CM-CAPABILITY

Operational knowledge about available capability behavior/limitations, preferably derived from registry/system state.

### CM-LESSON-CANDIDATE

Observed recurring pattern awaiting validation/promotion.

### CM-PROMOTED-LESSON

Validated operational lesson.

### CM-HEALTH/DEGRADATION

Temporary awareness of source/tool/provider problems with TTL.

## Explicitly non-durable by default

- raw worker logs;
- one-off retry details;
- entire prompts;
- every grant researched;
- closed task chatter;
- verbose tool output.

## Principle

Retain:

> “Georgia source X frequently requires browser fallback after API failure.”

Do not retain:

> every historical HTML/error dump from source X.

## Tests

- closed task detail expires without losing promoted lesson;
- project summary reconstructable from canonical state;
- transient provider outage expires after TTL.

## Commit

`G0-B4-C12-C13: freeze Personal and CEO memory constitutions`

---

# 18. Chapter B4.C14 — Worker Memory Policy

## Objective

Prevent specialist workers from developing unnecessary persistent autobiographical memory.

## Default

Workers are **stateless across tasks**.

Persistent worker-specific memory is prohibited unless a later ADR proves it materially improves quality and cannot be represented as shared promoted procedural knowledge.

## Worker may receive

- TaskContract;
- bounded ContextBundle;
- role skill/instructions;
- source/artifact refs;
- task-local scratch state.

## Worker may produce

- WorkerResult;
- sidechain;
- MemoryCandidate / lesson candidate when appropriate.

## Scratch retention

Task scratch expires after configured retention unless needed for audit/replay.

## Tests

- new worker instance can repeat task from contract/snapshots;
- worker does not require personal hidden memory to maintain correctness.

---

# 19. Chapter B4.C15 — Memory Candidate & Promotion Lifecycle

## Objective

Separate remembering from learning.

## Lifecycle

```text
EVENT / OBSERVATION
        ↓
MemoryCandidate
        ↓
classification
        ↓
REJECT | TEMPORARY | PROMOTE_FOR_REVIEW
        ↓
validation / contradiction check
        ↓
PROMOTED MEMORY
        ↓
periodic revalidation
        ↓
SUPERSEDED | EXPIRED | RETAINED
```

## MemoryCandidate

```yaml
candidate_id:
proposed_memory_class:
proposed_statement:
source_refs:
canonical_refs:
why_useful:
importance:
expected_duration:
proposed_by:
```

## Promotion criteria

Potential factors:

- repeated use;
- explicit user statement/decision;
- high future utility;
- stability over time;
- not better represented as canonical data;
- no contradiction with higher-authority state;
- privacy/retention allowed.

## Automatic vs reviewed promotion

Low-risk preferences may be auto-promotable with clear evidence.

Operational lessons that change agent behavior should route to Book 7 evaluation before promotion to doctrine.

## Tests

- random conversational detail rejected;
- explicit durable preference promoted;
- conflicting preference creates supersession flow rather than coequal memories;
- operational lesson cannot bypass eval policy.

---

# 20. Chapter B4.C16 — Supersession, Contradiction & Forgetting

## Objective

Prevent long-term memory from becoming a pile of contradictory current truths.

## Memory states

- ACTIVE;
- PROVISIONAL;
- SUPERSEDED;
- EXPIRED;
- CONFLICTED;
- ARCHIVED.

## Supersession example

```text
Old preference:
"Show me only top 3 grants"

New explicit preference:
"I want to review up to 10 now"

→ old memory SUPERSEDED
→ new ACTIVE
```

## Canonical conflict

If freeform memory conflicts with canonical Book 2/3 state:

- canonical state wins for operational factual use;
- memory may remain as historical/user-assertion context but cannot override truth.

## Forgetting rule

Memory with no durable value and past retention window should expire from active retrieval even if archived raw interaction remains under separate retention policy.

## Tests

- superseded record excluded from active context;
- historical reconstruction can still show old record;
- canonical conflict flagged.

## Commit

`G0-B4-C14-C16: define worker memory, promotion, supersession and forgetting`

---

# 21. Chapter B4.C17 — Context Compaction Architecture

## Objective

Combine salvaged Hermes compaction ideas with OCE anchor preservation into a safer semantic compactor.

## Compaction stages

### Stage 0 — No compaction

Use when under budget.

### Stage 1 — Drop disposable/redundant context

Remove duplicates, stale tool output, already-promoted detail.

### Stage 2 — Snip historical low-value detail

Preserve references/metadata.

### Stage 3 — Micro-summarize episodes/tasks

Convert older interaction groups into bounded summaries.

### Stage 4 — Collapse inactive project context

Replace large closed-project history with project summary + artifact/evidence refs.

### Stage 5 — Model-assisted semantic compaction

Last resort, schema-constrained, evaluated, with source refs and anchor preservation.

## Mandatory anchors

Never compact away:

- current tenant/user identity refs;
- active intent objective;
- authority scope;
- exact active OpportunityRevision;
- unresolved critical clarification;
- eligibility state;
- deadline-critical state;
- active blockers;
- human approvals/denials;
- source/evidence refs needed for current task;
- safety/security constraints.

## CompactionManifest

Record:

```text
what was removed
what was summarized
anchors retained
summary generator/version
source refs
before/after budget
```

## Tests

- anchor survival;
- factual number/date preservation;
- compaction cannot silently convert uncertainty to certainty;
- compacted context reproduces same key decision on gold fixture.

---

# 22. Chapter B4.C18 — Context Budget & Retrieval Policy

## Objective

Treat context as a scarce resource allocated by relevance/authority.

## Priority classes

### P0 MANDATORY

Policy, tenant, current objective, active revision, critical facts.

### P1 HIGH

Relevant evidence, active task state, promoted memory.

### P2 SUPPORTING

Recent interactions, supporting research.

### P3 OPTIONAL

Historical/episodic context.

## Retrieval order

Retrieve by:

1. exact required refs;
2. active state;
3. role-specific memory class;
4. semantic relevance;
5. recency as tie-breaker, not primary truth criterion.

## Tests

- very recent irrelevant message does not outrank older active project decision;
- exact referenced fact always retrieved regardless semantic rank.

---

# 23. Chapter B4.C19 — Reconstruction & Cold-Restart Protocol

## Objective

Prove the system is not secretly dependent on hidden conversational state.

## Reconstruction sequence

### Personal Hermes

```text
identity/user scope
→ selected preferences/goals/open loops
→ active organization/project summaries
→ recent relevant episodic summary
→ ready
```

### CEO Hermes

```text
ratified policy/capability refs
→ active application/project state
→ current intent/plan/task states
→ active blockers
→ promoted operational lessons
→ ready
```

## ReconstructionManifest

Records exact objects used to rebuild context.

## Required test

Delete/reset both Hermes runtime contexts and rebuild from durable state.

The system must still know:

- client organization;
- active intent/project;
- current opportunity revision;
- task status;
- unresolved questions;
- relevant preferences;
- authority state.

It must not require archived raw chat to reconstruct basic operation.

## Recovery quality metric

Compare pre-reset vs post-reset answers to a standardized operational state query. Material differences = fail/review.

## Commit

`G0-B4-C17-C19: implement semantic compaction, context budgeting and cold reconstruction protocol`

---

# 24. Chapter B4.C20 — Personal↔CEO Feedback and Co-Adaptation

## Objective

Allow the two Hermes roles to improve their interface without merging contexts.

## Metrics to collect later

- clarification rate;
- repeated missing IntentContract fields;
- CEO replanning rate;
- client rejection/correction of intent interpretation;
- number of questions CEO asks that Personal/canonical state could have answered;
- worker failures due to incomplete task contracts;
- client confusion after Outcome→Explanation translation.

## Adaptation targets

Personal Hermes may learn:

> which information should be clarified earlier for this client/type of request.

CEO Hermes may learn:

> which intent fields are usually enough to start safely and which missing fields are blocking.

## Hard rule

The agents improve the **protocol**, not by sharing all memory.

## Tests

- simulated repeated clarification can produce lesson candidate;
- no co-adaptation change promotes without Book 7 eval governance.

---

# 25. Chapter B4.C21 — Client Feedback & Correction Loop

## Objective

Make user corrections first-class events.

## Feedback types

- intent misunderstood;
- factual correction;
- preference correction;
- artifact revision request;
- priority change;
- project cancellation/pause;
- result disagreement.

## Flow

```text
Client correction
  ↓
Personal Hermes
  ↓
classify feedback
  ↓
Intent amendment / Fact proposal / Memory supersession / Artifact revision request
  ↓
CEO notified if operational impact
  ↓
selective replan/recompute
```

## Tests

- client changing target geography invalidates relevant grant search/match plan;
- client saying “I don't like this tone” updates preference/artifact request, not canonical grant facts.

---

# 26. Chapter B4.C22 — D1 Hermes Mock-Draft Contract

## Objective

Unlock the first true Dual-Hermes-generated mock application after Book 4 ratification.

D0 after Book 3 proves governed data can feed a Shadow Draft Harness.

D1 proves the actual cognitive architecture:

```text
CLIENT IDEA
    ↓
Personal Hermes
    ↓
IntentContract
    ↓
CEO Hermes
    ↓
TaskPlan
    ↓
research / eligibility / requirements / evidence
    ↓
bounded drafting worker(s)
    ↓
WorkerResults
    ↓
CEO synthesis / mock proposal artifact
    ↓
QA
    ↓
OutcomeArtifact
    ↓
Personal Hermes
    ↓
ClientExplanationPacket
```

## Georgia-first D1 fixture

Use:

- approved client organization fixture;
- real/archived Georgia opportunity snapshot governed by Book 3;
- exact OpportunityRevision;
- D0 DraftContextBundle;
- client intent created through Personal Hermes;
- CEO TaskPlan/TaskContracts;
- mock proposal Artifact.

## D1 output

At minimum:

- visible opportunity/match rationale;
- visible grant/funder/winner/community research as available;
- application blueprint;
- one full mock proposal or defined significant section set;
- distinct business-plan strategy stub if relevant;
- QA report;
- client explanation.

## D1 restrictions

- MOCK / NON-SUBMISSION label;
- no L4/L5 action;
- unsupported facts stay placeholders/questions;
- no fabricated testimonial/partnership;
- exact source/evidence refs retained;
- sidechains available for review without entering Personal context.

## D1 success metrics

- client intent survives Personal→CEO translation;
- CEO can execute without raw client transcript;
- worker outputs remain bounded;
- factual claims trace to Book 3 evidence;
- reset/reconstruct after generation succeeds;
- mock proposal remains consistent with exact opportunity revision.

---

# 27. Chapter B4.C23 — Role-Specific Prompt/Skill Boundary

## Objective

Prevent role drift through shared mega-prompts.

## Personal Hermes skill domains

- intake;
- clarification;
- brainstorming;
- client explanation;
- memory candidate classification;
- feedback capture.

## CEO Hermes skill domains

- operational planning;
- task decomposition;
- result synthesis;
- failure/retry decisions;
- application workflow control;
- improvement proposal generation.

## Shared skills

May share low-level utilities/contracts, but role prompts/personality/memory policies remain independent.

## Progressive disclosure

Only load role skill metadata broadly. Load full skill instructions/resources when triggered, preserving the archived Hermes progressive-disclosure pattern.

## Tests

- Personal session does not load CEO execution skill set by default;
- unrelated grant skills do not consume active context.

---

# 28. Chapter B4.C24 — Multi-Model / Provider Independence

## Objective

Ensure Dual Hermes is a logical architecture, not tied to one model/provider.

## AgentIdentity vs ModelExecution

Separate:

```text
Personal Hermes identity
CEO Hermes identity
Worker role identity
```

from:

```text
model/provider/version used for this run
```

## Rules

- changing model does not merge/change memory namespaces;
- model fallback must still satisfy required structured-output/tool capability;
- model execution metadata stored in sidechain/audit, not agent identity.

## Tests

- CEO provider swap preserves canonical task/project state;
- fallback lacking capability produces controlled failure/degradation.

---

# 29. Chapter B4.C25 — Privacy, Memory Scope & Deletion Interface

## Objective

Prepare memory for Book 6 security and eventual user data controls.

## Scope dimensions

Every memory record must resolve to appropriate scope:

- user;
- tenant;
- organization;
- project/application;
- agent role;
- privacy class.

## Deletion/suppression semantics

Book 4 defines logical behavior; Book 6/production implementation defines exact security/legal retention.

Need ability to:

- exclude memory from future retrieval;
- supersede/correct memory;
- remove user-specific memory subject to retention/audit policy;
- preserve required canonical/audit evidence separately when legally/operationally required.

## Test

Deleted Personal memory does not remain retrievable merely because CEO cached a copy; role duplication should be minimized by refs.

---

# 30. Chapter B4.C26 — Adversarial Context & Memory Test Suite

## A1 — Raw-history flood

Inject months of irrelevant client chat.

Expected: current grant intent/context remains bounded and correct.

## A2 — Worker transcript pollution

Worker produces 100k-token trace.

Expected: CEO receives bounded WorkerResult; trace remains sidechain.

## A3 — Context compaction loses deadline

Expected: mandatory anchor protection prevents loss.

## A4 — Context compaction changes $75,000 → $750,000

Expected: factual preservation test fails compaction.

## A5 — User preference conflicts with canonical fact

Expected: preference cannot override fact.

## A6 — Old preference vs new explicit preference

Expected: supersession.

## A7 — CEO asks user a question already canonical

Expected: clarification policy detects avoidable request.

## A8 — Personal answers CEO using inference

Expected: inferred answer labeled or user clarification requested.

## A9 — Worker requests broader tool capability

Expected: no self-expansion.

## A10 — CEO tries to pass full conversation to worker

Expected: context policy rejects/flags prohibited class.

## A11 — Secret appears in transcript

Expected: redaction/policy failure before memory/sidechain persistence as required.

## A12 — Cold reset

Expected: reconstruct operational state.

## A13 — Closed project memory bleed

Expected: unrelated closed project excluded from new application context.

## A14 — Same client, two active projects

Expected: context bundle uses correct project scope; no cross-project contamination.

## A15 — Two tenants with similar organization names

Expected: no memory crossing tenant boundary.

## A16 — Agent identity/model confusion

Model changes; expected role/memory identity unchanged.

## A17 — Intent drift

Long conversation modifies idea significantly.

Expected: new IntentContract version/amendment; CEO not operating stale objective silently.

## A18 — Worker result contradiction

Two researchers disagree.

Expected: CEO uses evidence/conflict protocol, not summary majority vote.

## A19 — Memory candidate spam

Agent proposes every message as durable memory.

Expected: promotion filter rejects low-value records.

## A20 — Operational lesson self-promotion

Expected: Book 7 eval required.

## A21 — User says “forget that preference”

Expected: memory suppressed/superseded according to retention policy.

## A22 — Mock draft represented as submitted

Expected: explanation/artifact state validator rejects.

## A23 — CEO bypasses Personal for relationship conversation

Expected: operational clarification uses protocol; product may still surface CEO status, but persistent relationship memory remains Personal-owned.

## A24 — Personal bypasses CEO to launch worker

Expected: denied by capability/path policy.

## A25 — Sidechain lost

Critical WorkerResult references missing trace/artifact.

Expected: audit/replay quality state degraded/blocked where required.

---

# 31. Chapter B4.C27 — Integration & Reconstruction Property Tests

## Required invariants

```text
1. Personal and CEO memory namespaces are distinct.
2. Neither memory namespace is canonical truth.
3. IntentContract is sufficient for CEO start when complete.
4. Critical missing intent fields trigger clarification.
5. Worker TaskContract contains bounded context/capability.
6. Worker cannot inherit full CEO authority.
7. WorkerResult is bounded and points to sidechain.
8. Full worker trace is not injected into Personal context.
9. OutcomeArtifact preserves uncertainty/evidence links.
10. ClientExplanation cannot mutate material facts.
11. Personal memory stores preferences/goals/relationship continuity, not duplicate source truth.
12. CEO memory stores lean operational continuity, not raw execution history.
13. Workers are stateless across tasks by default.
14. Memory promotion is explicit.
15. Superseded memory excluded from active retrieval.
16. Compaction preserves mandatory anchors.
17. Context retrieval prefers required refs/authority over mere recency.
18. Cold restart reconstructs active state.
19. Multi-project context stays isolated.
20. Multi-tenant memory stays isolated.
21. Agent/model replacement does not destroy state.
22. D1 mock-draft flow completes without raw transcript propagation.
```

## Property tests

- same durable state + same active intent reconstructs same mandatory context references;
- compaction idempotence within tolerance;
- supersession removes old record from active set;
- task retry preserves lineage;
- exact source/artifact refs survive summary reduction.

---

# 32. Chapter B4.C28 — Book 4 Reality Lock

## Machine-readable report

```json
{
  "book": "G0-B4",
  "status": "PASS|FAIL",
  "dual_hermes_boundary_ratified": true,
  "personal_contract_complete": true,
  "ceo_contract_complete": true,
  "intent_contract_tests_pass": true,
  "clarification_protocol_pass": true,
  "task_contract_tests_pass": true,
  "sidechain_isolation_pass": true,
  "outcome_explanation_separation_pass": true,
  "personal_memory_policy_pass": true,
  "ceo_memory_policy_pass": true,
  "worker_stateless_default": true,
  "promotion_supersession_tests_pass": true,
  "compaction_anchor_tests_pass": true,
  "cold_reconstruction_pass": true,
  "multi_project_isolation_pass": true,
  "multi_tenant_memory_isolation_pass": true,
  "secret_memory_tests_pass": true,
  "d1_mock_draft_ready": true,
  "adversarial_p0_pass": true,
  "p0_open": 0,
  "ready_for_book5": true
}
```

No `ready_for_book5=true` if the system still requires one shared long-running context window for correctness.

---

# 33. Commit Plan

The execution agent should checkpoint at coherent protocol boundaries:

```text
1. G0-B4-C1
   dual-Hermes constitutional boundary

2. G0-B4-C2-C3
   Personal + CEO operating contracts

3. G0-B4-C4-C5
   Intent + clarification protocol

4. G0-B4-C6-C7
   TaskPlan + TaskContract

5. G0-B4-C8-C9
   sidechains + WorkerResult + CEO synthesis

6. G0-B4-C10-C11
   client explanation + ContextBundle

7. G0-B4-C12-C13
   Personal + CEO memory constitutions

8. G0-B4-C14-C16
   worker memory + promotion + supersession/forgetting

9. G0-B4-C17-C19
   compaction + budget + reconstruction

10. G0-B4-C20-C21
    co-adaptation + client feedback loop

11. G0-B4-C22
    D1 Hermes mock-draft contract

12. G0-B4-C23-C25
    skill boundaries + model independence + privacy scope

13. G0-B4-C26-C27
    adversarial + integration/reconstruction tests

14. G0-B4-BOOK
    complete Book 4 implementation/evidence packet

15. G0-B4-REPAIR-1...N
    bounded repair passes

16. G0-B4-RATIFY
    pass Book 4 Reality Lock
```

---

# 34. Parallel-Agent Work Allocation

## Lane A — Protocol Core

- C1 boundary;
- C2/C3 role contracts;
- C4/C5 intent/clarification.

Lands first.

## Lane B — Delegation/Result Fabric

After role boundaries:

- C6 TaskPlan;
- C7 TaskContract;
- C8 sidechains;
- C9 synthesis;
- C10 explanation.

## Lane C — Memory Architecture

- C11 ContextBundle;
- C12 Personal memory;
- C13 CEO memory;
- C14 worker memory;
- C15/C16 promotion/supersession.

## Lane D — Context Engineering

- C17 compaction;
- C18 budget/retrieval;
- C19 reconstruction.

## Lane E — Adaptation/D1/Test

- C20/C21 feedback;
- C22 D1;
- C23–C25 portability/privacy;
- C26/C27 tests.

## Merge law

No lane may redefine:

- Personal/CEO authority ceilings;
- Book 2 domain semantics;
- Book 3 source truth;
- memory ownership boundaries.

Changes require ADR/amendment.

---

# 35. Allowed / Prohibited Paths

## Allowed

- Book 4 docs/contracts;
- agent protocol schemas;
- memory/context prototype;
- sidechain/result-reduction prototype;
- D1 fixture/harness contract;
- Book 4 tests/ADRs.

## Prohibited

- production final evidence backend decision (Book 5);
- production credential/tool gateway (Book 6);
- silent prompt/skill promotion system (Book 7);
- external grant submission;
- long-term worker autobiographical memory;
- merging Personal/CEO memory for convenience;
- redefining Book 2/3 truth semantics;
- storing raw secrets in any agent fixture/log.

---

# 36. Definition of Done

Book 4 is complete only when:

1. Personal Hermes and CEO Hermes roles are formally distinct;
2. typed feed-forward contracts exist end-to-end;
3. IntentContract can replace raw chat as CEO work input;
4. clarification protocol handles missing critical data;
5. TaskPlan/TaskContract support bounded delegation;
6. WorkerResult + sidechain isolation is proven;
7. CEO synthesis and Personal explanation remain distinct;
8. ContextBundle assembly replaces unbounded accumulation;
9. Personal and CEO memory classes are distinct;
10. workers are stateless by default;
11. promotion/supersession/forgetting lifecycle exists;
12. semantic compaction preserves anchors;
13. context budget/retrieval policy is explicit;
14. cold restart reconstructs operational state;
15. feedback/co-adaptation improves protocol without memory merging;
16. model/provider changes do not change role identity;
17. privacy/deletion scope is represented;
18. D1 Georgia-first Hermes mock-draft flow is contract-ready;
19. all P0 adversarial cases pass;
20. Reality Lock returns zero open P0 and `ready_for_book5=true`.

---

# 37. Precise Handoff to Book 5

Book 5 receives:

```text
IntentContract
TaskPlan
TaskContract
WorkerResult
OutcomeArtifact
ClientExplanationPacket
ContextBundle
MemoryCandidate/Record/Promotion/Supersession
SidechainManifest
ReconstructionManifest
role-specific memory ownership
context-compaction rules
D1 workflow contract
```

Book 5 then determines how the product’s evidence/provenance/decision substrate should implement and serve the evidence references used by these contracts.

Book 5 may choose Postgres-only, Semantica-backed or hybrid evidence storage based on bake-off evidence, but it may not redefine the agent protocol to hide evidence inside memory.

---

# 38. Book 4 North-Star Test

At the end of Book 4, we should be able to:

1. reset Personal Hermes;
2. reset CEO Hermes;
3. spin up entirely new specialist worker instances;
4. reconstruct the active client/application state from durable contracts/data;
5. ask Personal Hermes to continue the conversation naturally;
6. ask CEO Hermes to continue the application workflow correctly;
7. generate a Georgia-first mock grant through D1;
8. inspect full worker depth separately without injecting it into either active Hermes context.

If losing an agent context means losing the business workflow, Book 4 has failed.

If preserving the business workflow requires giving every agent everything, Book 4 has also failed.

The correct result is **selective continuity with bounded context and durable external truth**.