# Grant Sector — Dual-Hermes Architecture Context & R0 Salvage Charter

**Document ID:** GS-R0-CTX-001  
**Version:** 0.1  
**Status:** ACTIVE DISCOVERY BASELINE  
**Branch:** `grant-sector-r0-salvage`  
**Parent repository:** `dabiggestpoppa/larger-lab`  
**Date:** 2026-08-24  

---

## 0. Purpose

This document preserves the complete architectural intent established for the first commercial agent-system project: a governed Grant Intelligence and Application Production System built with enterprise-grade rigor comparable to Quant Lab/OCE, while intentionally reusing proven infrastructure, agent patterns, tooling, and build discipline already present across `larger-lab`, its historical branches, Hermes experiments, OCE work, and selected external open-source projects.

The immediate purpose is twofold:

1. prevent context loss while the architecture is still evolving; and
2. define the R0 deep-salvage pass that must occur before unnecessary rebuilding begins.

This document is not yet the final product constitution. It is the preserved working baseline that later G0 constitutional work must either ratify, refine, or explicitly supersede.

---

# 1. Product Identity

The system is **not** merely an AI grant writer.

It is a **governed Grant Intelligence + Application Production System** with an agentic operating layer.

Hermes is not the product itself. Hermes operates the product.

The product must eventually support:

- client intake and organization profile management;
- continuous grant discovery across relevant federal, state, foundation, and corporate sources;
- deterministic eligibility filtering;
- explainable grant matching and ranking;
- funder research;
- prior-winner / historical award research;
- demographic, impact, and community-needs research;
- evidence-backed application strategy;
- proposal generation;
- business-plan generation;
- financial/budget generation;
- pitch-deck generation;
- QA, factuality, consistency, citation, and humanization gates;
- human review and approval;
- later outreach / relationship workflows;
- later grant tracking and award-feedback learning.

The long-run platform should remain broader than grants so future Financial Literacy Framework sectors can reuse the platform kernel without inheriting grant-specific logic.

---

# 2. Core Architectural Decision — Dual Hermes

The system will use **two distinct Hermes agents** with separate responsibilities, context boundaries, memory policies, and authority.

This separation is deliberate. It protects quality by preventing one agent from becoming overloaded with both deep relationship context and high-volume operational execution context.

## 2.1 Hermes A — Personal / Client Agent

Primary role:

> Understand the client, help the client think, clarify intent, preserve relationship continuity, and translate natural conversation into structured intent.

Expected responsibilities:

- conversational assistant;
- brainstorming partner;
- clarification of ideas and goals;
- persistent understanding of the client and organization;
- preference tracking;
- open-loop tracking;
- idea refinement;
- explaining system results back to the client;
- producing structured intent packets for downstream execution.

Hermes A should **not** absorb raw execution transcripts or specialist-agent chatter.

Hermes A optimizes for understanding the person and business.

## 2.2 Hermes B — CEO / Application Operator

Primary role:

> Turn authorized intent into reliable system outcomes by planning, operating the application, delegating specialist work, evaluating results, handling retries, and improving workflows.

Expected responsibilities:

- accept normalized intent contracts;
- inspect canonical system state;
- create execution plans;
- delegate bounded tasks;
- operate Grant Intelligence Engine capabilities;
- supervise specialist agents;
- evaluate outputs;
- retry or escalate failures;
- synthesize final operational results;
- maintain lean operational continuity;
- prune stale execution context;
- promote only validated lessons into durable operational memory.

Hermes B optimizes for system execution, not personal relationship continuity.

## 2.3 Feed-Forward Interaction Model

Canonical flow:

```text
CLIENT
   │
   ▼
PERSONAL HERMES
   │
   │ interpretation / clarification
   ▼
INTENT ARTIFACT
   │
   ▼
OCE-DERIVED CONTROL PLANE
   │ validation / authorization / queue / audit
   ▼
CEO HERMES
   │
   │ decomposition / orchestration
   ▼
TASK CONTRACTS
   │
   ▼
SPECIALIST AGENTS / DETERMINISTIC SERVICES
   │
   │ evidence / results
   ▼
CEO HERMES
   │
   │ synthesis
   ▼
OUTCOME ARTIFACT
   │
   ▼
PERSONAL HERMES
   │
   │ client-appropriate explanation
   ▼
CLIENT
```

Key anti-pollution rules:

- full specialist transcripts do not enter Personal Hermes context;
- entire client conversation history does not enter worker context;
- CEO execution traces do not remain permanently inside CEO prompt context;
- worker agents receive bounded task contracts, not full organizational history;
- system truth lives outside Hermes memory;
- agent memory may be reset without destroying the business state.

---

# 3. Three-Plane System Model

## 3.1 Relationship Plane

Owned primarily by Personal Hermes.

Contains:

- client conversation;
- client preferences;
- organization understanding;
- goals;
- unresolved ideas;
- personal working style;
- relationship context;
- client-facing explanation.

Primary output: **Intent Contract**.

## 3.2 Control Plane

Owned by OCE-derived governance and CEO Hermes.

Contains:

- workflow state;
- task planning;
- authorization;
- policy;
- agent orchestration;
- context pruning;
- audit;
- evaluation;
- retries;
- evidence tracking;
- system health;
- cost control.

Primary output: **Task Contracts** and **Outcome Artifacts**.

## 3.3 Work Plane

Owned by deterministic services and bounded specialist agents.

Contains:

- grant-source ingestion;
- normalization;
- eligibility;
- matching;
- funder research;
- prior-winner research;
- impact research;
- evidence retrieval;
- application planning;
- proposal/business-plan/financial/deck production;
- QA.

Workers must remain replaceable and non-sovereign.

---

# 4. Memory Doctrine

## 4.1 General Principle

**Infinite memory is not the objective. Selective continuity is.**

The system should learn by retaining validated structure and useful conclusions, not by hoarding every token ever generated.

## 4.2 Personal Hermes Memory

Persistent but curated categories:

- organization identity;
- stable user preferences;
- active and long-term goals;
- important relationships;
- important decisions;
- unresolved open loops;
- promoted episodic summaries.

Proposed promotion lifecycle:

```text
Conversation
   ↓
Candidate memory
   ↓
Importance / recurrence / contradiction check
   ↓
Canonical memory
```

Superseded facts must be demoted or replaced rather than allowed to coexist as hidden contradictions.

## 4.3 CEO Hermes Memory

Much leaner and operationally focused.

Durable categories:

- system doctrine;
- workflow rules;
- active projects;
- active failures/blockers;
- known capabilities;
- known limitations;
- recent performance state;
- promoted operational lessons;
- policies.

Proposed retention posture:

```text
RAW EXECUTION WORK
TTL: hours to days

TASK SUMMARIES
TTL: days to weeks

PROJECT STATE
until project closure / archival

VALIDATED LESSONS
persistent only after promotion

SYSTEM DOCTRINE
persistent and versioned
```

The system should retain lessons rather than execution garbage.

Example:

Bad durable memory:

> Worker 7 returned a 6,000-token malformed HTML dump on a certain date.

Useful durable lesson:

> Source X frequently returns malformed HTML; use parser B and fallback C.

---

# 5. Authority Doctrine

No Hermes instance is authoritative system truth.

- Personal Hermes owns relationship continuity, not canonical operational truth.
- CEO Hermes owns governed orchestration, not sovereign authority.
- specialist agents own bounded work, not policy.
- canonical system truth belongs in OCE-derived state and durable stores.

Proposed CEO authority ladder:

- **L0 OBSERVE** — read system state;
- **L1 PROPOSE** — prepare actions without execution;
- **L2 SAFE EXECUTE** — research, match, and generate drafts;
- **L3 MANAGED EXECUTE** — modify governed project/application state;
- **L4 EXTERNAL ACTION** — send approved outreach / external communications;
- **L5 SUBMISSION** — submit grant application or equivalent high-consequence action.

Early product posture should emphasize L0-L2, with tightly bounded L3. L4 belongs to later outreach capability and L5 should remain explicitly gated.

---

# 6. OCE Relationship

OCE patterns are to be reused as the control philosophy and likely as selected implementation infrastructure.

The system should preserve these OCE principles:

- operator/client remains final human authority for consequential actions;
- no agent statement is self-validating;
- evidence and artifacts remain distinct;
- bounded agent authority;
- fail-closed behavior;
- source precedence;
- contradiction handling;
- decision records;
- drift audits;
- promotion/demotion of claims;
- task lineage;
- learning ledgers;
- worker isolation;
- auditability;
- reproducibility;
- Postgres as durable operational truth where appropriate;
- Redis or equivalent transport is not sole truth;
- recoverability is demonstrated, not assumed.

Existing Hermes/OCE gateway work should be treated as a high-priority salvage candidate rather than rebuilt blindly.

---

# 7. Intent Packet Boundary

Personal Hermes should translate conversational ideas into structured packets rather than forwarding raw chat.

Illustrative schema:

```yaml
intent_id: ...
client_id: ...
organization_id: ...
intent_type: explore_program_funding
objective: ...
constraints:
  geography: ...
  budget: ...
  timeline: ...
  hiring_constraints: ...
known_facts:
  - ...
open_questions:
  - ...
requested_action: ...
confidence: ...
source_conversation_refs:
  - ...
authority_scope: research_only
```

The exact schema will be designed later, but the boundary itself is binding for current planning.

---

# 8. CEO Task Contract Boundary

CEO Hermes should delegate structured tasks rather than forwarding whole context windows.

Illustrative task contract:

```yaml
task_id: ...
project_id: ...
worker_role: funder_research
objective: ...
inputs:
  canonical_profile_ref: ...
  grant_ref: ...
  evidence_refs: [...]
constraints:
  source_freshness: ...
  geography: ...
required_outputs:
  - structured_research_pack
  - citations
quality_gates:
  - no_unsupported_claims
  - current_source_required
expires_at: ...
authority: read_only_external_research
```

Full worker execution history should live in sidechain/audit storage, not CEO active context.

---

# 9. Specialist-Agent Philosophy

Specialist agents are bounded roles, not miniature sovereign applications.

Initial logical roles may include:

- intake normalization;
- discovery/source ingestion;
- funder research;
- prior-winner research;
- impact/demographic research;
- application architecture;
- proposal drafting;
- business-plan drafting;
- deck generation;
- citation/factuality review;
- alignment review;
- style/humanization review.

Deterministic services should own:

- eligibility logic once normalized;
- date arithmetic;
- totals and percentages;
- budgets and financial reconciliation;
- required-document checklists;
- workflow-state transitions;
- schema validation;
- final requirement coverage checks where deterministic rules exist.

---

# 10. Product Architecture Principle

Do not treat LLMs as database, source of record, or eligibility engine.

The application should be built around canonical typed data and versioned evidence.

Long-run major subsystems:

- organization/profile domain;
- grant opportunity domain;
- source adapter fabric;
- deterministic eligibility kernel;
- matching/ranking engine;
- research intelligence;
- evidence graph;
- application factory;
- QA gauntlet;
- artifact system;
- audit/evaluation system;
- human review interface;
- later outreach engine;
- later grant tracker and outcome-feedback engine.

---

# 11. Evidence Graph Principle

Important generated claims should maintain lineage to sources and artifact versions.

Minimum conceptual fields:

- claim;
- source;
- source URL/document identity;
- retrieval date;
- geography / population scope where relevant;
- confidence;
- permitted use;
- artifacts / sections in which claim appears;
- version lineage;
- verification state.

Changing evidence should make downstream dependency relationships observable.

---

# 12. Matching Philosophy

Grant matching should be a staged constraint funnel rather than a single opaque similarity score.

Proposed sequence:

```text
Opportunity universe
  ↓
Current/source validity
  ↓
Hard eligibility
  ↓
Geography / org type
  ↓
Funding-use compatibility
  ↓
Mission compatibility
  ↓
Impact/community alignment
  ↓
Historical winner alignment
  ↓
Funding-size suitability
  ↓
Application effort / expected value
  ↓
Ranked actionable queue
```

Every material ranking component should be explainable to the user.

---

# 13. Application Factory Principle

Large proposals should not be generated as single monolithic prompts.

Preferred pipeline:

```text
Application Blueprint
  ↓
Section Specifications
  ↓
Evidence Retrieval
  ↓
Draft Section
  ↓
Section Critic
  ↓
Factuality Check
  ↓
Alignment Check
  ↓
Cross-Document Consistency
  ↓
Document Compilation
```

Proposal, business plan, deck, financials, goals, and supporting documents should be linked by shared canonical facts so one edit can trigger selective regeneration of dependent artifacts.

---

# 14. QA Doctrine

The system should eventually include hard gates for:

- eligibility;
- source integrity;
- factual consistency;
- requirement coverage;
- numerical integrity;
- cross-document consistency;
- funder alignment;
- impact/evidence strength;
- hallucination detection;
- completeness;
- style/humanization;
- human approval.

AI-detection tools may be used as advisory signals if required by client process, but should not be treated as proof of authorship or factual quality.

---

# 15. Reuse Philosophy

Before building a new capability, investigate whether it already exists in:

1. current `larger-lab/main`;
2. `master`;
3. historical/archived branches;
4. Hermes archive states;
5. `hermes-set-up`;
6. OCE Golden System work;
7. generic `tools/` infrastructure;
8. mature external open-source projects.

Do not marry entire repositories by default. Harvest capabilities.

Every candidate capability should receive one disposition:

- **ADOPT** — use largely as-is;
- **FORK** — preserve upstream and develop our own branch/project;
- **WRAP** — keep upstream untouched behind our adapter;
- **PORT** — move a bounded capability into the new platform;
- **REWRITE** — retain idea/contract but replace implementation;
- **REJECT** — do not use;
- **DEFER** — useful later, not now.

---

# 16. R0 — Deep Salvage & Technology Archaeology Mandate

R0 must occur before serious new implementation.

The goal is to determine what reusable capability, architecture, operational knowledge, and code already exists.

## 16.1 Branches / areas that require deep inspection

Priority inspection targets:

- `main`;
- `master`;
- `execution-runtime-foundation`;
- `hermes-set-up`;
- `archive/hermes-02e51f11`;
- `archive/hermes-262c2f34`;
- `archive/hermes-cde01a2a`;
- `archive/pruned-master-2026-08-15`;
- `archive/review-branch`;
- OCE Block 0/1 and related current branches;
- `.agents/` and agent skills;
- `.hermes/` histories;
- `.openclaw*` where reusable patterns exist;
- `tools/`;
- workflow / cron / orchestration utilities;
- memory and context-management utilities;
- evaluation / adversarial testing systems;
- MCP gateways and tool facades;
- browser/scraping/research tooling;
- document/PDF/artifact-generation utilities;
- schemas and validation layers;
- observability, audit, security, backup, and recovery infrastructure.

## 16.2 Explicit R0 skip rule

Pure trading-domain logic may be skipped unless it contains clearly reusable infrastructure.

Examples primarily to skip as domain logic:

- MVE trading model;
- capital-routing trading logic;
- crypto strategies/data logic;
- CEREBUS-specific strategies;
- market execution logic;
- trading signal engines.

However, if those branches contain generic reusable infrastructure such as queueing, task orchestration, data validation, artifact management, experiment tracking, evaluation, worker control, scheduling, caching, APIs, observability, or fail-closed patterns, those generic capabilities should still be salvaged conceptually or technically.

## 16.3 R0 questions for every candidate

For each capability/project/tool, record:

- what problem does it solve?
- is it generic or domain-specific?
- current branch/source location;
- implementation language/runtime;
- dependency footprint;
- tests present?
- security posture;
- evidence of working state;
- maintenance status;
- architecture quality;
- context/memory implications;
- Hermes compatibility;
- OCE compatibility;
- MCP compatibility;
- multi-user / tenant implications;
- portability to new repository;
- coupling to trading domain;
- hidden technical debt;
- whether code, contract, or only idea is worth keeping;
- ADOPT/FORK/WRAP/PORT/REWRITE/REJECT/DEFER disposition;
- reason for disposition.

## 16.4 Expected R0 outputs

R0 should end with at least:

1. **Branch Archaeology Map** — what each relevant branch contains and why it matters.
2. **Reusable Capability Registry** — component-level salvage decisions.
3. **Hermes Salvage Map** — memory, workflow, MCP, skill, sidechain, maintenance, and operating patterns.
4. **OCE Salvage Map** — governance, runtime, evidence, worker, audit, and infrastructure patterns.
5. **Tools Salvage Map** — generic utilities worth porting or wrapping.
6. **Reject/Do-Not-Port Ledger** — prevents old baggage from quietly entering the new product.
7. **Gap Map** — capabilities not already solved internally.
8. **External Research Queue** — only after internal salvage is understood.
9. **Recommended Seed Architecture** — which proven pieces become the starting skeleton.
10. **G0 Input Packet** — facts and decisions passed forward into formal product constitution.

---

# 17. Existing High-Value Candidates Already Identified

The following are already high-priority salvage candidates and require deeper validation:

## 17.1 Hermes context-compaction skill

Historical Hermes work contains a five-stage context-compaction design:

- budget reduction;
- older-history snipping;
- micro-compaction;
- context collapse;
- model-generated auto-compaction as last resort.

This directly supports the Dual-Hermes memory doctrine.

## 17.2 Hermes subagent sidechain manager

Historical Hermes work contains a sidechain pattern where:

- parent receives only a summary;
- full worker transcript is retained separately;
- JSONL sidechain preserves auditability;
- parent context pollution is reduced.

This is a likely foundational pattern for CEO Hermes worker delegation.

## 17.3 Hermes workflow system

Historical Hermes work contains chief-of-staff style scheduled workflows and Telegram delivery patterns. These may provide reusable scheduling, workflow, and operator-interface ideas.

## 17.4 OCE-Hermes Telegram Operator branch

`hermes-set-up` contains an OCE/Hermes operator project with:

- isolated Hermes profile;
- MCP facade;
- JSON schema validation;
- rate limiting;
- credential redaction;
- request IDs;
- structured audit logging;
- explicit state vocabulary;
- Docker Compose;
- runbooks;
- threat model;
- disaster recovery;
- secret rotation;
- adversarial/security tests;
- integration/unit tests.

Its current observer-only architecture already embodies the key rule that Hermes operates through OCE rather than bypassing system authority.

## 17.5 Current generic `tools/`

Current main already includes generic agent and workflow infrastructure such as:

- agent hooks;
- agent onboarding;
- error analysis;
- architecture-aware commit tools;
- cron/workflow utilities;
- chat summarization;
- chat synchronization;
- Claude/Hermes MCP integration utilities;
- other generic tooling to be inventoried during R0.

---

# 18. New Repository Strategy — Deferred Until R0

A new GitHub repository is desired for the eventual client/product build, but it should **not** be created blindly before salvage decisions determine the correct seed skeleton.

Current working approach:

- preserve discovery and architecture on branch `grant-sector-r0-salvage` inside `larger-lab`;
- complete R0 archaeology;
- identify exact components/contracts to transplant;
- then create the clean product repository;
- import only deliberate, documented, traceable pieces.

The new repository should not inherit Quant Lab trading baggage simply because `larger-lab` is the current research source.

---

# 19. R0 Operating Rule

R0 prioritizes depth over speed.

Do not perform a filename-only inventory and call it salvage.

For high-value candidates, inspect actual implementation, tests, configuration, architecture notes, and lineage. Compare branches where necessary. Identify obsolete experiments, duplicated tools, partially working prototypes, and genuinely production-worthy components.

The purpose is to avoid two failure modes:

1. rebuilding infrastructure that already exists and works; and
2. importing legacy complexity that only appears reusable from surface inspection.

---

# 20. Immediate Next Action

Perform the full R0 deep dive, starting with:

1. `master` versus `main` architectural differences;
2. all three archived Hermes branches;
3. `execution-runtime-foundation` generic agent infrastructure;
4. `archive/pruned-master-2026-08-15` and review/archive branches;
5. `hermes-set-up` implementation-level review;
6. main `tools/`, `.agents/`, OCE docs/runtime, workflow, evaluation, security, observability, and infrastructure;
7. only after internal salvage is mapped, build external open-source research queue.

Pure trading logic may be skipped except where generic infrastructure is embedded inside it.

---

**Preservation rule:** If later architecture changes, preserve this document as lineage. Do not overwrite historical intent without a new version or explicit supersession record.
