# G0 Entry Plan — Grant Sector Constitutional Design

**Document ID:** GS-G0-PLAN-001  
**Version:** 0.1  
**Status:** READY TO BEGIN AFTER R0 RATIFICATION  
**Date:** 2026-08-24

---

## 0. Objective

G0 converts R0 discoveries into the binding constitution and interface contracts for the Grant Intelligence + Application Production System.

R0 answered:

- what internal infrastructure is reusable;
- what external components are worth evaluating;
- what grant-domain data exists;
- what should remain platform-owned;
- which historical patterns must be rejected.

G0 answers:

> What is allowed to exist in the production architecture, what is authoritative, how components communicate, and what evidence is required before implementation can advance?

No broad implementation begins until G0 closes.

---

# 1. G0.0 — R0 Ratification

Freeze the R0 findings into an authority packet.

Inputs:

- Dual-Hermes context/charter;
- salvage map;
- branch archaeology;
- reject/do-not-port ledger;
- external repo reviews;
- grant-domain data/source deep hunt;
- updated gap map;
- updated seed architecture.

Outputs:

- ratified R0 findings;
- unresolved-decision ledger;
- selected prototype/bake-off candidates;
- explicit non-goals.

Exit gate:

- no unresolved contradiction about product boundaries or R0 source hierarchy.

---

# 2. G0.1 — Product Constitution & Authority

Define binding laws for:

- operator/client authority;
- Personal Hermes authority;
- CEO Hermes authority;
- specialist-worker authority;
- deterministic service authority;
- source authority;
- canonical database authority;
- evidence promotion;
- human approval;
- external actions;
- self-improvement/change governance.

Must codify the L0-L5 authority ladder and fail-closed defaults.

Exit gate:

- every consequential operation has an identifiable authority owner and approval policy.

---

# 3. G0.2 — Domain Ontology & CommonGrants Mapping

Define canonical entities and relationships:

- Organization;
- Person/Team role where needed;
- Funder;
- Grant Opportunity;
- Program/Assistance Listing;
- Eligibility Rule;
- Eligibility Decision;
- Award;
- Recipient;
- Application Project;
- Requirement;
- Budget;
- Canonical Fact;
- Evidence Claim;
- Statistic Observation;
- Artifact;
- Outcome/Feedback.

Create explicit CommonGrants Opportunity/Application/Award mappings.

Exit gate:

- domain model is internally coherent and CommonGrants compatibility is documented/testable.

---

# 4. G0.3 — Grant Intelligence Data Constitution

Freeze:

- `SourceRegistry`;
- `SourceSnapshot`;
- `ExternalIdentifier`;
- `StatisticObservation`;
- source revision/change event;
- source precedence;
- source freshness;
- evidence confidence;
- conflict resolution/escalation;
- data retention;
- provenance requirements.

Initial authoritative source classes:

- Grants.gov/Simpler;
- SAM Assistance Listings;
- USAspending;
- IRS/FAC;
- Census/SAIPE;
- state/public portals;
- curated/private/Candid;
- governed web sources.

Exit gate:

- no promoted external fact can exist without defined source lineage/freshness semantics.

---

# 5. G0.4 — Dual-Hermes Protocol & Memory Constitution

Freeze schemas for:

- `IntentContract`;
- `ClarificationRequest`;
- `TaskPlan`;
- `TaskContract`;
- `WorkerResult`;
- `OutcomeArtifact`;
- `ClientExplanationPacket`;
- `FeedbackCorrectionEvent`.

Freeze memory policies:

- Personal memory classes;
- CEO memory classes;
- WORK/LEARNED/KNOWLEDGE promotion;
- TTL/retention;
- supersession;
- context budgets;
- sidechain retention;
- reconstruction requirements;
- prohibited secret/sensitive memory behavior.

Exit gate:

- feed-forward path is schema-defined and no role needs unbounded upstream context.

---

# 6. G0.5 — Evidence / Semantica Decision

Run a bounded evidence-layer bake-off:

### Candidate A
Product-owned relational/provenance implementation using Postgres and internal contracts.

### Candidate B
Semantica-backed graph/provenance/reasoning implementation behind the same product contracts.

Test on real domain cases:

- solicitation amendment conflict;
- one grant → multiple historical awards;
- nonprofit rename with stable EIN;
- conflicting private/official source;
- statistic with vintage/geography constraints;
- claim→source→application-section lineage;
- decision replay after source revision.

Evaluate:

- correctness;
- explainability;
- temporal replay;
- conflict detection;
- query complexity;
- performance;
- operational burden;
- tenant isolation;
- backup/recovery;
- exit cost.

Exit gate:

- Evidence Graph substrate selected by evidence rather than preference.

---

# 7. G0.6 — Security / Identity / Tool Authority

Freeze:

- tenant boundary;
- organization membership;
- agent/service identity;
- RBAC/ABAC/capability model;
- credential vault rules;
- Treg-inspired tool gateway contract;
- Hermes MCP boundary;
- outbound network policy;
- PII/data classification;
- secret redaction;
- audit actor/event model;
- high-consequence confirmation policy.

Exit gate:

- threat model has no unresolved P0 path allowing agent bypass of product authority or tenant boundaries.

---

# 8. G0.7 — Evaluation & Promotion Doctrine

Freeze the test/promotion framework for:

- source adapters;
- parsing;
- intent translation;
- eligibility extraction;
- deterministic eligibility;
- matching;
- winner research;
- evidence promotion;
- community statistics;
- proposal generation;
- QA critics;
- source conflicts;
- tool security;
- memory pruning/reconstruction.

Tooling candidates:

- Hermes Skill Eval Lab;
- Promptfoo;
- selected Guardrails validators;
- adversarial fixtures from OCE harness.

Every model/prompt/skill/workflow change gets:

```text
BASELINE
   vs
CANDIDATE
   ↓
assertions + adversarial cases + human review
   ↓
quality / cost / latency / variance
   ↓
PROMOTE | REVISE | REJECT
```

Exit gate:

- every high-value nondeterministic component has a measurable promotion rule.

---

# 9. G0.8 — First Vertical Slice Contract

Freeze a single production-shaped test path using real sources:

```text
Personal Hermes
  ↓
Intent Contract
  ↓
CEO Hermes
  ↓
Grants.gov/Simpler
  ↓
Source Snapshot
  ↓
SAM ALN enrichment
  ↓
Eligibility
  ↓
USAspending winner/history
  ↓
IRS/FAC organization context
  ↓
ACS/SAIPE evidence
  ↓
Evidence Graph
  ↓
Explainable Match
  ↓
Application blueprint + selected sections
  ↓
QA
  ↓
Human Review
  ↓
Personal Hermes explanation
```

Optional secondary source proof:

- California state opportunity; or
- one private/foundation Crawl4AI source.

Exit gate:

- end-to-end contracts are implementable without architectural exceptions.

---

# 10. G0.9 — Clean Repository Seed Specification

Only after G0.0-G0.8:

- create new production repository;
- preserve R0/G0 docs as imported lineage;
- create platform/agents/sectors/grants structure;
- import only ratified salvage packages;
- pin third-party components;
- initialize schemas/migrations/tests/evals/infra;
- create ADRs for every external dependency;
- configure branch protection/CI/security scanning.

No entire `larger-lab` branch is copied.

Exit gate:

- repository can be recreated from the ratified seed manifest and contains no trading baggage or archived secret state.

---

# 11. G0 Ratification Deliverable

At close, produce a `G0_RATIFICATION_PACKET` containing:

- constitution;
- domain ontology;
- CommonGrants mapping;
- source/data constitution;
- authority/capability matrix;
- Dual-Hermes protocol;
- memory policy;
- evidence architecture decision;
- security threat model;
- evaluation doctrine;
- vertical-slice specification;
- clean-repo seed manifest;
- unresolved/deferred decisions;
- G1 implementation plan.

**G1 begins only when this packet is internally consistent and passes the G0 reality lock.**
