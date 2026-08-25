# G0 Full Master Build Blueprint

**Document ID:** GS-G0-MASTER-001  
**Version:** 1.0  
**Status:** READY FOR CONTINUOUS BOOK-BY-BOOK EXECUTION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-24

---

# 0. Purpose

This blueprint is the complete floor plan for G0. It is designed for continuous execution by an agent or engineering worker **one full book at a time**, followed by independent review/repair before the next book begins.

The workflow is intentionally asymmetric:

1. architecture and acceptance criteria are planned in advance;
2. execution agent builds one complete book continuously;
3. reviewer verifies evidence, tests, contracts, and contradictions;
4. defects generate a repair pass;
5. only after book ratification does the next book begin.

The purpose is to create a flywheel where planning stays stable and work quality improves through evidence-backed review instead of repeatedly re-planning the whole system.

---

# 1. G0 Book Set

G0 consists of ten books:

- **Book 0 — R0 Ratification & Reality Lock**
- **Book 1 — Product Constitution & Authority**
- **Book 2 — Grant Domain Ontology & CommonGrants Interoperability**
- **Book 3 — Grant Intelligence Data Constitution**
- **Book 4 — Dual-Hermes Protocol & Memory Constitution**
- **Book 5 — Evidence, Provenance & Decision Substrate**
- **Book 6 — Security, Identity & Tool Authority**
- **Book 7 — Evaluation, Promotion & Quality Doctrine**
- **Book 8 — First Production-Shaped Vertical Slice Contract**
- **Book 9 — Clean Repository Seed & G1 Handoff**

Each book is independently reviewable and has its own reality lock.

---

# 2. Global Book Execution Protocol

Every book uses the same execution lifecycle:

```text
PLAN
  ↓
BUILD ALL CHAPTERS
  ↓
RUN CHAPTER TESTS
  ↓
RUN BOOK INTEGRATION TESTS
  ↓
PRODUCE EVIDENCE PACKET
  ↓
COMMIT BOOK CHECKPOINT
  ↓
INDEPENDENT REVIEW
  ↓
REPAIR PASS IF REQUIRED
  ↓
BOOK REALITY LOCK
  ↓
RATIFY / BLOCK
```

No book may silently change the invariants of a ratified previous book. Any required change must be made through a supersession/ADR record and re-run affected tests.

Each work packet must state:

- book/chapter ID;
- authoritative inputs;
- allowed paths;
- prohibited paths;
- implementation objective;
- required deliverables;
- required tests;
- commit checkpoint;
- exit gate;
- escalation conditions.

---

# 3. Global Commit Discipline

Each book gets:

1. chapter-level checkpoints for meaningful contract boundaries;
2. one book-complete checkpoint before review;
3. optional repair commits after review;
4. one ratification commit after reality lock.

Naming convention:

```text
G0-B<book>-C<chapter>: <short description>
G0-B<book>-BOOK: complete Book <book> implementation
G0-B<book>-REPAIR-<n>: <repair summary>
G0-B<book>-RATIFY: pass Book <book> reality lock
```

Do not squash away repair lineage during G0.

---

# 4. Global Evidence Packet Standard

Every book must produce:

```text
BOOK_PLAN
IMPLEMENTED_ARTIFACTS
SCHEMAS / CONTRACTS
TEST_FIXTURES
TEST_RESULTS
ADVERSARIAL_RESULTS
DECISION / ADR REGISTER
KNOWN_LIMITATIONS
DEFERRED_ITEMS
OPEN_ISSUES
REPAIR_HISTORY
REALITY_LOCK_REPORT
NEXT_BOOK_HANDOFF
```

A book is not complete because code or documents exist. It is complete only when evidence proves the exit gate.

---

# BOOK 0 — R0 Ratification & Reality Lock

## Mission

Convert exploratory R0 findings into one authoritative decision baseline.

## Chapters

### B0.C1 — R0 Artifact Manifest

Build a canonical manifest of every R0 file, version, commit, authority class and supersession relationship.

Deliverables:

- artifact manifest Markdown;
- machine-readable manifest YAML/JSON;
- link/commit validator.

Tests:

- all referenced artifacts exist;
- no duplicate artifact IDs;
- supersession chains are acyclic;
- every authority artifact has version and status.

Commit after C1.

### B0.C2 — Decision Register

Normalize all R0 conclusions into:

- RATIFIED;
- RATIFIED_WITH_CONDITION;
- PROTOTYPE_REQUIRED;
- DEFERRED;
- REJECTED;
- UNRESOLVED.

Deliverables:

- decision register;
- machine-readable register;
- source reference for every decision.

Tests:

- every major R0 conclusion appears once;
- every decision has rationale/source/status;
- no contradictory duplicate decisions.

Commit after C2.

### B0.C3 — Contradiction & Drift Sweep

Identify contradictions across R0 documents.

Classes:

- authority;
- storage;
- source truth;
- memory;
- component disposition;
- security;
- licensing;
- data semantics;
- phase timing.

Deliverables:

- contradiction ledger;
- severity classification;
- closure records.

Tests:

- deliberate contradiction fixtures fail;
- zero unresolved P0 contradiction.

Commit after C3.

### B0.C4 — Non-Goal Freeze

Freeze exclusions and anti-scope-creep rules.

Deliverables:

- non-goals document;
- prohibited architecture paths;
- deferred complexity list.

Tests:

- every G0/G1 plan can be checked against non-goals;
- known excluded features do not appear as mandatory dependencies.

### B0.C5 — Prototype/Bake-Off Register

Freeze bounded candidates needing evidence.

Candidates include:

- Semantica vs relational evidence substrate;
- Unstructured vs existing parser fabric;
- PixelRAG fallback;
- Crawl4AI;
- GPT Researcher patterns;
- Promptfoo/Hermes Eval Lab;
- Univer;
- Activepieces.

Deliverables:

- hypothesis;
- baseline;
- success metrics;
- kill criteria;
- responsible later book.

Commit after C4–C5.

### B0.C6 — R0 Ratification Reality Lock

Machine-computed readiness gate.

Must assert:

- zero P0 contradictions;
- all major findings classified;
- all prototype candidates bounded;
- production boundary explicit;
- no stale authority artifact silently active.

Book 0 final commit, review, repairs, ratification commit.

---

# BOOK 1 — Product Constitution & Authority

## Mission

Create the binding guiding principles and executable authority model for the system.

**Important:** Book 1 may be drafted immediately from established principles. Book 0 exists to ratify its inputs and catch contradictions, not to prevent writing the constitution. The constitution begins as a provisional v0.x draft and becomes binding only after Book 0 ratification and Book 1 tests pass.

## Chapters

### B1.C1 — Constitutional Preamble & System Purpose

Define:

- product mission;
- client sovereignty;
- relationship plane, control plane, work plane;
- Hermes role distinction;
- grant platform vs Hermes distinction;
- commercial/multi-tenant posture;
- future Financial Literacy Framework extensibility.

Deliverables:

- constitutional preamble;
- system-purpose statement;
- explicit non-sovereign agent clause.

### B1.C2 — Constitutional Laws

Freeze laws including:

1. canonical truth lives outside agent memory;
2. bounded authority;
3. deterministic supremacy for deterministic constraints;
4. evidence before promotion;
5. human approval for consequential external action;
6. agent replaceability;
7. secrets separation;
8. no silent self-modification;
9. full consequential-action auditability;
10. fail closed on ambiguity;
11. tenant isolation;
12. source/version lineage;
13. reversible promotion where possible;
14. workers are disposable/non-sovereign;
15. no hidden authority inherited from tool availability.

Deliverables:

- constitution laws;
- law IDs;
- rationale;
- machine-reference mapping.

Commit after C1–C2.

### B1.C3 — Actor Catalog

Actors:

- Human Client;
- Human Admin/Operator;
- Personal Hermes;
- CEO Hermes;
- Specialist Worker;
- Deterministic Service;
- Source Adapter;
- Policy Engine;
- Database;
- Artifact Store;
- External Integration;
- future Outreach Agent;
- future Submission Agent.

Define for each:

- identity;
- purpose;
- default authority;
- forbidden actions;
- audit expectations.

### B1.C4 — L0–L5 Authority Ladder

Freeze levels:

- L0 Observe;
- L1 Propose;
- L2 Safe Execute;
- L3 Managed Execute;
- L4 External Action;
- L5 Submission/Legally Material.

Define initial actor-level ceilings.

Commit after C3–C4.

### B1.C5 — Capability Registry

Typed capability model.

Initial families:

- organization.*;
- opportunity.*;
- source.*;
- eligibility.*;
- match.*;
- research.*;
- evidence.*;
- application.*;
- budget.*;
- artifact.*;
- qa.*;
- communication.*;
- submission.*;
- system.*.

Every capability defines actor, level, scope, approval, side effects, audit and failure semantics.

### B1.C6 — Human Approval Constitution

Action classes:

- no approval;
- review-after;
- approval-before;
- dual approval;
- prohibited in phase.

### B1.C7 — Self-Improvement Governance

Freeze:

```text
observation → candidate lesson → candidate change → sandbox/eval → review → promote/revise/reject → monitored rollout → rollback
```

CEO may propose improvements but cannot silently alter production policy/code/prompts.

### B1.C8 — Failure / Escalation Law

Define:

- FAIL_CLOSED;
- DEGRADE_TO_READ_ONLY;
- RETRY_BOUNDED;
- ESCALATE_HUMAN.

Commit after C5–C8.

### B1.C9 — Executable Policy Stub

Implement schema/config for actor, capability, authority grant, approval policy.

Prototype:

```text
decide(actor, capability, resource, tenant, context)
→ ALLOW | DENY | REQUIRE_APPROVAL
```

### B1.C10 — Constitution Adversarial Tests

Tests:

- unknown actor denied;
- unknown capability denied;
- worker cannot escalate itself;
- CEO at L2 cannot submit;
- Personal Hermes cannot mutate CEO-only state;
- source adapter cannot alter organization truth directly;
- missing tenant denied;
- tool availability cannot bypass policy;
- secret cannot be stored in agent memory fixture;
- policy mutation without ADR blocked.

### B1.C11 — Book 1 Reality Lock

Must prove 100% of consequential capability classes have explicit authority, scope, approval and audit semantics.

Book complete commit → review → repairs → ratification.

---

# BOOK 2 — Grant Domain Ontology & CommonGrants Interoperability

## Mission

Freeze the language and identity of every core business object.

## Chapters

### B2.C1 — Entity Boundary Decisions

Resolve:

- Organization/Funder/Recipient roles;
- Program vs Opportunity;
- ApplicationProject vs interoperable Application;
- CanonicalFact vs EvidenceClaim;
- Artifact vs SourceSnapshot;
- Person/contact/member boundaries.

Deliverables:

- boundary ADRs;
- ontology map.

### B2.C2 — Core Entity Definitions

Define:

- Organization;
- Person;
- Funder;
- Program/Assistance Listing;
- GrantOpportunity;
- EligibilityRule;
- EligibilityDecision;
- Award;
- ApplicationProject;
- Requirement;
- Budget;
- CanonicalFact;
- EvidenceClaim;
- StatisticObservation;
- Artifact;
- OutcomeFeedback.

Commit after C1–C2.

### B2.C3 — Identity & External-Identifier Semantics

Stable internal IDs independent of provider IDs.

Support:

- rename;
- DBA/aliases;
- same name/different EIN;
- revisions;
- cross-source award IDs;
- geography identities.

### B2.C4 — Relationship Catalog

Define typed allowed relationships and endpoint classes.

### B2.C5 — Domain State Machines

State machines for:

- Opportunity;
- EligibilityDecision;
- ApplicationProject;
- Requirement;
- Artifact;
- OutcomeFeedback.

Commit after C3–C5.

### B2.C6 — CommonGrants Mapping

Map internal models to CommonGrants Opportunity/Application/Award.

Field classes:

- EXACT;
- EXTENSION;
- INTERNAL_ONLY;
- EXTERNAL_ONLY;
- LOSSY.

### B2.C7 — Schema Prototypes

Pydantic/JSON Schema drafts + fixtures.

### B2.C8 — Domain Invariants

Examples:

- conflicted fact cannot masquerade as verified;
- application points to exact opportunity revision;
- award recipient resolves to Organization;
- monetary values use decimal/fixed-point;
- timestamps timezone-aware;
- source-backed objects retain lineage.

### B2.C9 — Domain Test Suite

Tests:

- identity merge/split;
- state transitions;
- invalid relation rejection;
- CommonGrants round trip;
- extension preservation;
- lossy mapping reporting;
- opportunity revision linkage;
- conflicted fact behavior.

### B2.C10 — Book 2 Reality Lock

No P0 ambiguity in entity boundaries, identities, relationships or public mapping.

Commit → review → repair → ratify.

---

# BOOK 3 — Grant Intelligence Data Constitution

## Mission

Define how external reality is registered, captured, revised, trusted, conflicted, aged and promoted.

## Chapters

### B3.C1 — SourceRegistry

Fields include source identity, class, authority tier, jurisdiction, access mode, auth, freshness, terms, adapter version and health.

### B3.C2 — SourceSnapshot

Immutable source state with raw object URI/hash, retrieval/effective times, adapter/parser versions, previous snapshot and revision key.

### B3.C3 — ExternalIdentifier Catalog

Namespaces:

- EIN;
- UEI;
- ALN;
- Grants.gov opportunity number;
- FAIN;
- USAspending award ID;
- SAM IDs;
- FIPS;
- state IDs;
- CommonGrants IDs.

### B3.C4 — StatisticObservation

Typed quantitative evidence with geography, population, reference period, dataset/version, margin of error/methodology and source snapshot.

Commit after C1–C4.

### B3.C5 — Source Authority / Precedence Matrix

Tier A–E source hierarchy with fact-class-specific precedence.

### B3.C6 — Freshness Constitution

Soft-stale, hard-stale, on-demand refresh, deadline-near refresh and dataset-vintage semantics.

### B3.C7 — Revision / Change Protocol

Define SourceChangeEvent and P0/P1/P2 materiality.

P0 triggers downstream invalidation/re-evaluation.

### B3.C8 — Conflict Resolution Protocol

Possible states:

- auto-precedence;
- merge-compatible;
- unresolved;
- refresh-required;
- human escalation;
- critical-use blocked.

### B3.C9 — Evidence Confidence Model

No subjective LLM confidence as sole evidence.

Use source authority, directness, extraction quality, normalization confidence, corroboration, freshness, contradiction state and geography/population fit.

Commit after C5–C9.

### B3.C10 — Data Retention & Deletion Classes

Canonical state, snapshots, artifacts, sidechains, audits, temporary caches, PII.

### B3.C11 — Provenance Chain

```text
SourceRegistry → SourceSnapshot → extraction/normalization → fact/claim/statistic → decision/research/match → application/artifact
```

### B3.C12 — Real-Source Fixtures

At minimum fixture-backed:

- Grants.gov/Simpler;
- USAspending or Census.

### B3.C13 — Data Adversarial Tests

Tests:

- source amendment;
- stale cache conflict;
- hostile webpage instruction;
- missing raw snapshot;
- LLM-generated statistic without source;
- geography mismatch;
- equal-authority conflict;
- duplicate/invalid identifier.

### B3.C14 — Book 3 Reality Lock

Every promoted external fact must be traceable to immutable source state with freshness/authority semantics.

Commit → review → repair → ratify.

---

# BOOK 4 — Dual-Hermes Protocol & Memory Constitution

## Mission

Freeze the exact feed-forward protocol between client cognition, operational cognition and workers.

## Chapters

### B4.C1 — Personal Hermes Contract

Purpose, capabilities, forbidden actions, conversation role, relationship memory.

### B4.C2 — CEO Hermes Contract

Purpose, operational authority, task orchestration, pruning, improvement proposals, forbidden direct DB/secret behavior.

### B4.C3 — IntentContract

Schema for translating client conversation into bounded operational intent.

### B4.C4 — ClarificationRequest

CEO→Personal request without contaminating contexts.

### B4.C5 — TaskPlan & TaskContract

Typed bounded work packets.

### B4.C6 — WorkerResult & Sidechain

Short parent result + full separate trace.

### B4.C7 — OutcomeArtifact & ClientExplanationPacket

CEO synthesis vs Personal client-facing explanation.

Commit after C1–C7.

### B4.C8 — Personal Memory Constitution

Identity, preferences, goals, relationships, decisions, open loops, episodic summaries.

### B4.C9 — CEO Memory Constitution

System state, active projects, failures, capabilities, limitations, promoted lessons, policies.

### B4.C10 — WORK / LEARNED / KNOWLEDGE Promotion

Candidate→promotion→supersession/demotion rules.

### B4.C11 — Context Compaction

Combine Hermes compaction, sidechains, anchor preservation and archive-first summarization.

### B4.C12 — Reconstruction Doctrine

System should reconstruct operational truth after Hermes reset using canonical stores.

### B4.C13 — Memory / Context Tests

- no client raw history dumped to workers;
- no worker trace dumped to Personal;
- CEO survives compaction;
- Personal preference retained after episodic compression;
- superseded fact removed from active memory;
- secret memory injection rejected;
- reset/rebuild succeeds.

### B4.C14 — Book 4 Reality Lock

Feed-forward schema complete and no role requires unbounded upstream context.

---

# BOOK 5 — Evidence, Provenance & Decision Substrate

## Mission

Select and freeze the implementation substrate for evidence lineage, conflicts, temporal state and decision replay.

## Chapters

### B5.C1 — Product Evidence Interface

Freeze product-owned interfaces before choosing backend.

### B5.C2 — Candidate A: Relational/Postgres Prototype

Implement bounded evidence graph/provenance semantics using relational model.

### B5.C3 — Candidate B: Semantica Prototype

Implement same contracts on Semantica.

### B5.C4 — Bake-Off Dataset

Cases:

- solicitation amendment;
- grant→historical awards;
- nonprofit rename/stable EIN;
- equal-authority conflict;
- statistic vintage/geography;
- claim→section lineage;
- decision replay.

### B5.C5 — Comparative Benchmarks

Correctness, explainability, temporal replay, conflict detection, query complexity, performance, operational burden, tenant isolation, backup/recovery, exit cost.

### B5.C6 — Decision ADR

Choose:

- Postgres-only;
- Semantica-backed;
- hybrid.

### B5.C7 — Evidence API / Contract Freeze

### B5.C8 — Book 5 Reality Lock

Evidence backend selected by tests rather than preference.

---

# BOOK 6 — Security, Identity & Tool Authority

## Mission

Prevent agent/tool capability from bypassing tenant, authority or secret boundaries.

## Chapters

### B6.C1 — Tenant Model

Organization membership, user roles, service identities, tenant-resource scoping.

### B6.C2 — RBAC/ABAC/Capability Model

Map actor identity + capability + resource + context.

### B6.C3 — Credential Vault Constitution

No raw secrets in Hermes, sidechains, prompts, logs or Git.

### B6.C4 — Treg-Inspired Tool Gateway

Registry, injector/proxy, health, audit, credential scoping.

### B6.C5 — Hermes MCP Boundary

Filtered facade; no direct database/service bypass.

### B6.C6 — Network / Egress Policy

Allowed external hosts, source classes, browser restrictions.

### B6.C7 — Data Classification / PII

### B6.C8 — Prompt/Tool Injection Defense

Especially web/document research.

### B6.C9 — Audit Event Model

Actor, tenant, capability, target, request ID, approval, result, evidence.

### B6.C10 — Threat Model

### B6.C11 — Adversarial Security Tests

- cross-tenant read/write;
- tool escalation;
- credential exfiltration;
- prompt injection from source;
- malicious attachment;
- direct DB attempt;
- external send without approval;
- stale/revoked capability.

### B6.C12 — Book 6 Reality Lock

Zero unresolved P0 bypass path.

---

# BOOK 7 — Evaluation, Promotion & Quality Doctrine

## Mission

Make every important nondeterministic component measurable and promotable through evidence.

## Chapters

### B7.C1 — Eval Corpus Architecture

Versioned gold sets, adversarial fixtures, human-review samples.

### B7.C2 — Hermes Eval Lab Port

Candidate vs baseline workflow.

### B7.C3 — Promptfoo Integration

Regression, prompt injection, tool red-team.

### B7.C4 — Guardrails / Structured Validation

Selected validators only.

### B7.C5 — Source Adapter Evals

Accuracy, freshness, schema, replay, dedupe.

### B7.C6 — Intent Translation Evals

Completeness, clarification rate, semantic correctness.

### B7.C7 — Eligibility Extraction & Deterministic Eval Tests

### B7.C8 — Matching Evals

Precision@k, recall, explanation correctness.

### B7.C9 — Research / Winner Evidence Evals

Unsupported claim rate, citation support, source authority.

### B7.C10 — Application Generation Evals

Requirement coverage, factuality, alignment, contradictions, human revision burden.

### B7.C11 — Memory / Reconstruction Evals

### B7.C12 — Promotion Policy

PROMOTE / REVISE / REJECT thresholds, rollback.

### B7.C13 — Cost/Latency/Variance Metrics

### B7.C14 — Book 7 Reality Lock

Every high-value nondeterministic component has a measurable promotion rule.

---

# BOOK 8 — First Production-Shaped Vertical Slice Contract

## Mission

Specify one real, minimal end-to-end path that proves the architecture.

## Chapters

### B8.C1 — Vertical Slice User Scenario

A real organization/client intent and one real federal opportunity.

### B8.C2 — Personal→CEO Handoff

### B8.C3 — Grants.gov/Simpler Ingestion

### B8.C4 — SAM Program Enrichment

### B8.C5 — Deterministic Eligibility

### B8.C6 — USAspending Winner/History Research

### B8.C7 — IRS/FAC Organization Context

### B8.C8 — ACS/SAIPE Community Evidence

### B8.C9 — Evidence Graph Promotion

### B8.C10 — Explainable Match

### B8.C11 — Application Blueprint + Selected Sections

### B8.C12 — QA/Human Review

### B8.C13 — Client Explanation

### B8.C14 — Optional Secondary Source Proof

California state source or one private/foundation Crawl4AI source.

### B8.C15 — Vertical Slice Acceptance Tests

- no context pollution;
- deterministic/replayable eligibility;
- full evidence lineage;
- accepted task survives restart;
- source revision invalidation;
- cost/latency visibility;
- audit completeness;
- human approval works;
- end-to-end reconstruction.

### B8.C16 — Book 8 Reality Lock

Contracts implementable without architectural exception.

---

# BOOK 9 — Clean Repository Seed & G1 Handoff

## Mission

Create the clean production repository only after all prior G0 contracts are ratified.

## Chapters

### B9.C1 — Seed Manifest

List every file/package to transplant/build and exact source lineage.

### B9.C2 — Repository Structure

```text
apps/
platform/
agents/
sectors/grants/
schemas/
migrations/
infra/
tests/
evals/
docs/
```

### B9.C3 — Third-Party Dependency ADRs

Pin version/commit/license/role/exit strategy.

### B9.C4 — Import Ratified Salvage

Only selected OCE/Hermes/Research Mesh components.

### B9.C5 — Initial Schemas/Migrations

### B9.C6 — CI / Security / Branch Protection

### B9.C7 — Reproducible Local Environment

### B9.C8 — Seed Verification

No trading baggage, no archived secrets, all ratified contracts present.

### B9.C9 — G1 Build Backlog

Translate vertical slice into implementation chapters.

### B9.C10 — G0 Final Ratification Packet

Contains all books, ADRs, tests, reality locks and unresolved/deferred decisions.

### B9.C11 — G0 Final Reality Lock

Only if PASS does G1 begin.

---

# 5. Cross-Book Dependency Graph

```text
BOOK 0  R0 RATIFICATION
  ↓
BOOK 1  CONSTITUTION / AUTHORITY
  ↓
BOOK 2  DOMAIN ONTOLOGY
  ↓
BOOK 3  DATA CONSTITUTION
  ↓
BOOK 4  DUAL-HERMES PROTOCOL / MEMORY
  ↓
BOOK 5  EVIDENCE SUBSTRATE
  ↓
BOOK 6  SECURITY / IDENTITY / TOOLS
  ↓
BOOK 7  EVAL / PROMOTION
  ↓
BOOK 8  VERTICAL SLICE CONTRACT
  ↓
BOOK 9  CLEAN REPO / G1 HANDOFF
```

Some prototype work may be prepared early, but ratification proceeds in dependency order.

---

# 6. Reviewer Flywheel

After the execution agent completes one book, the reviewer should not redo the build. Review should use this sequence:

1. inspect book commit range;
2. compare implementation to master blueprint;
3. verify required deliverables exist;
4. run/inspect test evidence;
5. search for contradictions against previously ratified books;
6. identify P0/P1/P2 defects;
7. issue bounded repair packet;
8. verify repair commits;
9. re-run book reality lock;
10. ratify or block next book.

Recommended review output:

```text
BOOK STATUS
PASS | PASS_WITH_REPAIR | FAIL

P0
...

P1
...

P2
...

TEST GAPS
...

CONTRADICTIONS
...

REPAIR PACKET
...

READY_FOR_NEXT_BOOK
true|false
```

---

# 7. Agent Continuous-Execution Rule

The worker agent may execute an entire book continuously without waiting for chapter-by-chapter approval **provided**:

- it remains inside allowed paths;
- it follows the frozen book plan;
- it commits at specified checkpoints;
- it does not alter prior ratified invariants;
- it does not skip tests because implementation appears correct;
- it records unresolved uncertainty instead of inventing authority;
- it stops on P0 contradiction or required external decision.

This is the intended operating model for G0.

---

# 8. Master Definition of Done

G0 is done when all ten books are ratified and the final G0 Reality Lock proves:

- zero unresolved P0 contradiction;
- constitutional authority executable;
- domain contracts stable;
- CommonGrants interoperability proven;
- source/provenance semantics complete;
- Dual-Hermes protocol bounded;
- agent memory reconstructable/non-authoritative;
- evidence substrate selected by bake-off;
- security has no unresolved P0 bypass;
- nondeterministic components have promotion tests;
- vertical slice fully specified;
- clean repo reproducible;
- G1 backlog derives directly from ratified contracts.

At that point planning stops being the bottleneck. G1 becomes implementation against a known floor plan.