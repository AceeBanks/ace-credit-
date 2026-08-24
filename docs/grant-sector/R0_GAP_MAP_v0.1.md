# R0 Gap Map

**Document ID:** GS-R0-GAP-001  
**Version:** 0.1  
**Status:** INTERNAL SALVAGE BASELINE COMPLETE  
**Date:** 2026-08-24

---

## 0. Purpose

This map identifies what the Grant Sector product still needs after deep internal salvage. A gap does not automatically mean “build from scratch.” It means the capability is not sufficiently solved by currently inspected `larger-lab` assets and should enter either fresh design or external due diligence.

---

# 1. Domain-Critical Gaps — Build Ourselves

These capabilities are the product moat and should not be outsourced wholesale to generic agent frameworks.

| Gap | Why internal salvage is insufficient | Recommended ownership |
|---|---|---|
| Canonical Organization Profile model | No grant/business tenant model exists | **NEW BUILD** |
| Canonical Grant Opportunity model | Research-paper models are not grant semantics | **NEW BUILD** |
| Grant eligibility DSL / normalized rule model | No deterministic grant rule engine exists | **NEW BUILD** |
| Eligibility evaluator | Must be deterministic/explainable after extraction | **NEW BUILD** |
| Explainable grant matching model | Existing routers/retrieval are not grant ranking | **NEW BUILD** |
| Grant-specific evidence hierarchy | Academic citation scoring is wrong domain | **NEW BUILD** |
| Funder / award / past-winner domain model | No equivalent internal domain | **NEW BUILD** |
| Grant Evidence Graph schema | Old generic graph is too broad | **NEW BUILD using salvaged graph concepts** |
| Application Project state machine | Existing task states are too low-level | **NEW BUILD** |
| Application blueprint / section dependency graph | No internal grant compiler | **NEW BUILD** |
| Cross-document fact registry | Needed to synchronize proposal/deck/financials | **NEW BUILD** |
| Budget / financial reconciliation engine | Must be deterministic and grant aware | **NEW BUILD** |
| Grant requirement coverage engine | Needs grant-specific checklist/rubric parsing | **NEW BUILD** |
| Human review / approval gates | OCE gives governance pattern, not product UX | **NEW BUILD** |
| Outcome/award feedback model | No grant lifecycle tracking domain | **NEW BUILD with Phase 3 hooks from day one** |

---

# 2. External Due-Diligence Gaps

These should be researched externally before custom implementation because mature solutions may already exist.

## 2.1 Grant-source connectivity

Need current evaluation of:

- Grants.gov APIs/feeds;
- SAM/assistance-related federal data where applicable;
- state/local opportunity sources;
- foundation databases and licensing constraints;
- corporate grant pages;
- historical federal award sources;
- IRS/nonprofit/public organization data where applicable;
- philanthropic award datasets.

Questions:

- API or scrape?
- terms/license?
- source freshness?
- revision/deadline semantics?
- rate limits?
- stable identifiers?
- historical winner data availability?

## 2.2 Browser / web research automation

Historical workspace contains browser/scraping skills, but no inspected component is yet promoted as a production Grant browser fabric.

Research mature candidates for:

- robust browser automation;
- anti-fragile extraction;
- source snapshots;
- structured web extraction;
- robots/terms-aware crawling;
- retry/replay;
- web-page change detection.

Prefer wrapping a mature browser layer rather than embedding site-specific browser logic into Hermes.

## 2.3 Production document compiler

Open Design is promising for visual artifacts, but a deterministic enterprise document compiler is still a gap.

Need evaluation for:

- DOCX templating;
- PDF generation;
- section/page controls;
- tables/charts;
- reusable styles;
- headers/footers;
- citations/footnotes;
- tracked versions;
- stable rendering;
- editable client deliverables.

## 2.4 Spreadsheet / financial artifact generation

Need robust XLSX/CSV generation and formula validation integrated with canonical budget facts.

## 2.5 Multi-tenant auth / identity

OCE historically assumes a private single-operator environment. Commercial product needs:

- tenant isolation;
- user/org memberships;
- roles;
- service identities;
- scoped authorization;
- audit actor identity;
- secure invitation/recovery flows.

Evaluate mature auth providers/libraries vs self-hosting.

## 2.6 Object/artifact storage

OCE Block 1 gives the architecture principle, but commercial product needs exact selection and lifecycle policy for:

- source snapshots;
- uploads;
- generated files;
- sidechains/traces;
- exports;
- encrypted backups.

## 2.7 Observability stack

OCE has metrics/tracing ideas and code, but production selection remains open:

- OpenTelemetry;
- logs;
- traces;
- model/tool cost telemetry;
- workflow SLIs;
- source-adapter health;
- error aggregation.

## 2.8 Evaluation / LLM observability tooling

Hermes skill-creator provides a strong internal eval pattern. External review should determine whether existing eval platforms can provide useful storage/UI/tracing without taking ownership of our evaluation logic.

---

# 3. Design Gaps — Internal Architecture Needed Before Tool Choice

## 3.1 Dual-Hermes communication protocol

Need exact schemas for:

- Intent Contract;
- Clarification Request;
- Task Plan;
- Task Contract;
- Worker Result;
- Outcome Artifact;
- Client Explanation Packet;
- Feedback/Correction Event.

## 3.2 Memory promotion and pruning engine

Internal patterns exist, but exact policy is still a design gap.

Need:

- Personal memory classes;
- CEO memory classes;
- candidate → promoted → superseded/demoted lifecycle;
- TTL rules;
- privacy classification;
- source/provenance links;
- contradiction resolution;
- reconstructability tests;
- context budgets.

## 3.3 Agent authority policy model

Need executable mapping of:

- agent/service identity;
- capability;
- tenant/project scope;
- resource target;
- risk class;
- approval required;
- expiry/revocation;
- audit obligations.

## 3.4 Source-trust policy

Need grant-domain precedence rules, e.g. current official solicitation vs cached page vs aggregator vs user statement.

## 3.5 Change/self-improvement governance

CEO Hermes may eventually improve workflows, prompts, or adapters. Need distinction between:

- observation;
- proposed lesson;
- candidate change;
- sandbox evaluation;
- approved promotion;
- rollback.

No production self-modification without gates.

---

# 4. UX Gaps

Need product designs for:

- organization intake / profile completeness;
- Personal Hermes chat;
- grant discovery dashboard;
- explainable match detail;
- visible past-winner/funder research;
- evidence viewer;
- application workspace;
- artifact/version diff;
- QA blockers;
- human approval;
- CEO Hermes activity/status without exposing noisy chain-of-thought or raw worker transcript;
- admin/audit view.

Historical OCE frontend and artifact builders may provide patterns, but product UX needs a clean design.

---

# 5. Security / Compliance Gaps

Before production pilot, explicitly design:

- data classification;
- tenant isolation tests;
- secret management;
- PII handling;
- retention/deletion;
- audit retention;
- source/document access control;
- encryption at rest/in transit;
- backup restore;
- dependency/SBOM scanning;
- prompt/tool injection defenses for web research;
- malicious document handling;
- outbound network policy;
- external action confirmations.

The archived secret-in-memory finding makes this a mandatory early gate, not cleanup work.

---

# 6. R0 Gap Priority

## P0 — must resolve in G0/G1

- canonical domain schemas;
- Dual-Hermes contracts;
- authority/policy model;
- source/evidence precedence;
- memory retention/promotions;
- tenant/auth architecture;
- Postgres truth model;
- source snapshot/artifact policy;
- security threat model.

## P1 — needed for first functional vertical slice

- federal/source adapter;
- parser/document ingestion;
- deterministic eligibility;
- match ranking;
- funder/winner/evidence research;
- evidence graph;
- proposal blueprint + one artifact path;
- QA/eval harness;
- Personal→CEO→worker→client feed-forward path.

## P2 — expand after vertical slice is evidence-backed

- broad source network;
- full business-plan/deck/financial artifact suite;
- advanced source change detection;
- additional model routing;
- enhanced dashboards;
- outreach hooks;
- grant tracking/outcome loop.

---

# 7. External Research Rule

External projects are candidates, not authorities.

Every external candidate must be scored on:

- license/commercial suitability;
- current activity;
- security posture;
- test quality;
- dependency burden;
- portability;
- API stability;
- data ownership;
- observability;
- tenant isolation;
- Hermes/MCP/OCE compatibility;
- replacement/exit cost;
- exact capability we want to harvest.

Do not select a large framework because it appears comprehensive. Prefer narrow components behind our contracts.