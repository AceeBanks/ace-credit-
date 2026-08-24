# R0 Seed Architecture Recommendation

**Document ID:** GS-R0-SEED-001  
**Version:** 0.2  
**Status:** RECOMMENDED INPUT TO G0 — DATA/SOURCE HUNT INCORPORATED  
**Date:** 2026-08-24

---

## 0. Decision

Do not seed the future Grant Sector repository from any one existing branch.

Create a clean repository after G0 ratifies the contracts, then transplant selected proven components behind new product interfaces.

The future product should be architected as a **domain-neutral governed platform kernel + Grant Sector module + two Hermes operator profiles + first-class Grant Intelligence Data Fabric**.

The deep grant-domain hunt adds one major interoperability principle:

> **Our internal grant model may be richer, but it should map cleanly to the HHS-backed CommonGrants protocol for Opportunities, Applications, and Awards wherever practical.**

---

# 1. Reference Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                       CLIENT EXPERIENCE                      │
│                                                              │
│  Web UI / Mobile-friendly Chat / Notifications              │
│                         │                                    │
│                         ▼                                    │
│              PERSONAL HERMES PROFILE                         │
│       relationship continuity + intent formation             │
└─────────────────────────┬────────────────────────────────────┘
                          │ Intent Contract
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                   GOVERNED CONTROL PLANE                     │
│                                                              │
│ Identity / Tenant / Policy / Audit / Event / Project State  │
│                          │                                   │
│                CEO HERMES PROFILE                            │
│               planner + application operator                 │
│                          │                                   │
│         pre-tool policy → execute → post-tool verify         │
└─────────────────────────┬────────────────────────────────────┘
                          │ Task Contracts
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                     WORKER / TOOL FABRIC                     │
│                                                              │
│ Research  Parser  Evidence  Proposal  QA  Artifact workers  │
│ Crawl/Deep Research/Validation/Integration capabilities      │
│                                                              │
│ Short result → CEO                                           │
│ Full trace → sidechain / audit storage                       │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│              GRANT INTELLIGENCE DATA FABRIC                 │
│                                                              │
│ Source Registry → Fetch/Snapshot → Normalize → Revisions    │
│                                                              │
│ Grants.gov / SAM / USAspending / IRS / FAC / Census         │
│ State portals / targeted foundation-corporate web sources    │
│ Optional Candid enrichment                                   │
│                                                              │
│ CommonGrants compatibility mappings                          │
└─────────────────────────┬────────────────────────────────────┘
                          │ typed facts + immutable evidence
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                       DOMAIN KERNEL                          │
│                                                              │
│ Org Profile   Grant Opportunity   Eligibility   Matching     │
│ Funder/Award  Evidence Graph      Application   Budget       │
│ Requirements  Artifact Facts      Outcome/Feedback           │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                     DATA / ARTIFACT PLANE                    │
│                                                              │
│ PostgreSQL authoritative operational state                  │
│ Object storage: raw source snapshots / uploads / artifacts   │
│ Redis optional transport/cache only                          │
│ Vector/graph retrieval attached to canonical identities      │
│ Observability / audit / backup / restore                     │
└──────────────────────────────────────────────────────────────┘
```

---

# 2. Seed Packages

## Package A — Hermes Operator Gateway

Source:

- `hermes-set-up/oce-hermes-telegram-operator`
- Treg architecture as a reference for server-side tool/credential proxying

Port/fork:

- isolated Hermes profiles;
- filtered MCP facade architecture;
- schema validation;
- service identity;
- redaction;
- rate limiting;
- request IDs;
- structured audit;
- capability matrix;
- threat-model/runbook structure;
- adversarial gateway tests.

Add:

- separate Personal and CEO Hermes profiles;
- tenant/project scope on capabilities;
- authority levels L0-L5;
- typed Tool Registry;
- server-side credential vault/injection;
- provider health and tool audit;
- no direct database or secret access from Hermes.

## Package B — Context Continuity Kernel

Sources:

- archived Hermes context compaction;
- archived Hermes subagent manager;
- OCE Structural Memory;
- OCE adaptive anchor preservation;
- current chat summarizer;
- Continuity Intelligence doctrine.

Build combined system:

```text
Raw event / conversation
        ↓
Archive / source trace
        ↓
Candidate memories / task summaries
        ↓
Policy + contradiction + importance checks
        ↓
WORK
        ↓ validated/persistent value
LEARNED
        ↓ promoted canonical lesson/fact
KNOWLEDGE
```

Personal and CEO Hermes use separate namespaces and promotion policies.

## Package C — Research Fabric

Sources:

- `master/core/research`;
- GPT Researcher planning/execution/publisher patterns;
- Crawl4AI for governed web extraction;
- optional SearXNG for discovery only.

Port:

- source-adapter interface;
- rate limiting;
- retry/backoff;
- dedupe principles;
- scheduler;
- ResearchTask state shape;
- lifecycle/heartbeat/retry/abandonment;
- token/cost accounting;
- evaluator architecture;
- synthesis pipeline.

Rewrite:

- persistence in Postgres;
- grant-specific worker roles;
- evidence evaluator;
- model routing;
- source-specific policies.

Research workers cannot directly promote raw web claims. Promotion requires a `SourceSnapshot` and evidence validation.

## Package D — Grant Intelligence Data Fabric

**New mandatory seed package after domain-source deep hunt.**

### Core contracts

- `SourceRegistry`
- `SourceSnapshot`
- `ExternalIdentifier`
- `StatisticObservation`
- source revision/change event
- normalized Opportunity/Award/Organization facts

### Initial source adapters

Federal opportunities:

- Grants.gov REST API;
- Simpler.Grants.gov where useful;
- SAM Assistance Listings.

Federal winner/history:

- USAspending;
- SAM subawards when needed;
- TAGGS for HHS specialization.

Organization/capacity:

- IRS EO BMF;
- IRS 990-series XML;
- Federal Audit Clearinghouse;
- ProPublica as convenience/enrichment.

Community evidence:

- Census ACS;
- Census SAIPE;
- BLS;
- BEA;
- one domain-specific layer selected by use case (CDC/USDA/NCES/HUD).

State/private:

- California Grants Portal as first state reference adapter;
- one targeted private/foundation source via Crawl4AI;
- Candid only as optional paid enrichment after coverage/ROI measurement.

### Key rule

Search/discovery is not evidence. Every promoted fact must resolve to an immutable source snapshot or approved structured dataset record.

## Package E — Evidence / Provenance Layer

Sources:

- Semantica P0 bake-off;
- historical OCE graph/provenance/contradiction concepts.

We own the Grant ontology. Semantica is evaluated as infrastructure for:

- claim→source provenance;
- conflicting facts;
- temporal state;
- decision chains;
- deterministic graph reasoning;
- entity relationships;
- auditable exports.

Canonical operational state still remains in product-owned storage; Semantica must not become an opaque sovereign truth source.

## Package F — Agent Governance Harness

Sources:

- OCE Block 0;
- Harness Engineering doctrine;
- pre/post hooks;
- context-map / orchestration skills.

Build:

- typed capability registry;
- policy decision point;
- action risk classes;
- pre-execution authorization;
- post-execution validation;
- stop/completion gate;
- audit event schema;
- approval flow;
- task/project checkpoints;
- source-trust/freshness policy;
- dependency invalidation after material source revisions.

## Package G — Agent Evaluation Lab

Sources:

- archived Hermes `skill-creator`;
- Promptfoo;
- selected Guardrails validators.

Generalize:

```text
candidate skill/prompt/workflow
        ↓
versioned eval corpus
        ↓
parallel candidate + baseline
        ↓
formal assertions + red-team + human review
        ↓
quality / latency / tokens / cost
        ↓
variance + regression analysis
        ↓
PROMOTE | REVISE | REJECT
```

Add domain eval suites for source adapters, winner research, community statistics, eligibility, source conflicts and application artifacts.

## Package H — Document / Artifact Ingestion

Sources:

- Parser Router architecture;
- MarkItDown / ODL-PDF / Chandra;
- Unstructured bake-off;
- PixelRAG as layout/visual fallback.

Build a stable `SourceDocument` adapter contract. Treat parser engines as replaceable workers.

## Package I — Financial / Client Artifact Output

Sources:

- Univer evaluation for editable/headless workbook workflow;
- Open Design/D2 for selected visual artifacts;
- separate deterministic proposal/document compiler remains product-owned.

Canonical facts and budget calculations must exist independently from rendered XLSX/DOCX/PDF/PPTX outputs.

---

# 3. CommonGrants Compatibility

The HHS CommonGrants protocol is now a design input, not a peripheral reference.

G0 should define explicit adapters:

```text
GrantOpportunity <-> CommonGrants Opportunity
ApplicationProject <-> CommonGrants Application
AwardOutcome <-> CommonGrants Award
```

Our internal models may include additional:

- evidence lineage;
- source snapshots;
- explainability fields;
- internal matching scores;
- worker/audit state;
- QA state;
- tenant policy;
- artifact dependencies.

Those fields should be namespaced/internal rather than contaminating the external interoperability contract.

---

# 4. New Product Packages

```text
platform/
    identity/
    policy/
    audit/
    events/
    tasks/
    memory/
    sources/
        registry/
        snapshots/
        identifiers/
        revisions/
    evidence/
    artifacts/
    models/
    observability/

agents/
    hermes-personal/
    hermes-ceo/
    skills/
    workers/
    evals/

sectors/grants/
    domain/
        organization.py
        opportunity.py
        funder.py
        award.py
        eligibility.py
        application.py
        requirement.py
        budget.py
        outcome.py
        statistics.py
    interoperability/
        commongrants/
    sources/
        grants_gov/
        simpler_grants/
        sam_assistance/
        usaspending/
        irs/
        fac/
        census/
        states/
        private_web/
        candid_optional/
    eligibility/
    matching/
    research/
    evidence/
    applications/
    qa/
```

---

# 5. Core Contracts to Freeze in G0

Before implementation, G0 should define/version at least:

1. `IntentContract`
2. `ClarificationRequest`
3. `TaskContract`
4. `WorkerResult`
5. `OutcomeArtifact`
6. `OrganizationProfile`
7. `GrantOpportunity`
8. `Funder`
9. `Award`
10. `EligibilityRule`
11. `EligibilityDecision`
12. `MatchExplanation`
13. `SourceRegistry`
14. `SourceSnapshot`
15. `ExternalIdentifier`
16. `StatisticObservation`
17. `SourceRevisionEvent`
18. `EvidenceClaim`
19. `ResearchPack`
20. `ApplicationProject`
21. `CanonicalFact`
22. `BudgetModel`
23. `RequirementChecklist`
24. `ArtifactManifest`
25. `QAReport`
26. `ApprovalDecision`
27. `AgentIdentity`
28. `CapabilityGrant`
29. `AuditEvent`
30. `MemoryCandidate/Promotion`
31. `FeedbackOutcome`
32. CommonGrants mapping contracts.

These contracts become the stable seams around which source providers, parsers, agents and external components can be swapped.

---

# 6. Source Truth and Revision Rules

G0 must make source precedence executable rather than descriptive.

Core principles:

- current official solicitation/amendment dominates older copies;
- current issuer source dominates aggregator claims for issuer-owned facts;
- official structured award/tax/statistical data outranks third-party summaries for the facts it owns;
- third-party/private datasets are enrichment, not silent overrides;
- search snippets never become promoted evidence;
- materially changed source snapshots trigger dependency re-evaluation;
- unresolved conflicts are visible and fail closed for consequential decisions.

Grant deadlines, eligibility, requested amounts and required attachments are material dependency fields.

---

# 7. First Real Vertical Slice — Updated

Do not use mocked grant-domain data except unit fixtures.

The first evidence-backed vertical slice should prove:

```text
Client idea/request
   ↓
Personal Hermes clarification
   ↓
Intent Contract
   ↓
CEO Hermes plan
   ↓
REAL Grants.gov/Simpler opportunity query
   ↓
SourceSnapshot + normalized GrantOpportunity
   ↓
SAM Assistance Listing enrichment
   ↓
Deterministic eligibility
   ↓
USAspending historical recipient/award research
   ↓
IRS/FAC organization verification/capacity context
   ↓
ACS/SAIPE community evidence
   ↓
Evidence Graph / Semantica bake-off
   ↓
Explainable match
   ↓
Application blueprint + selected proposal sections
   ↓
QA / Promptfoo-domain assertions / validators
   ↓
Human review
   ↓
Personal Hermes client explanation
```

Optional addition:

- one California state opportunity OR one targeted private foundation webpage through Crawl4AI to prove non-federal adapter extensibility.

### Required proof

- raw client chat is not unnecessarily passed to workers;
- worker traces do not pollute CEO active context;
- every promoted factual claim has source lineage;
- source snapshots are immutable/replayable;
- opportunity amendments are detected;
- eligibility is reproducible from normalized facts;
- award/winner research never implies causation without evidence;
- statistics retain geography/period/methodology/MOE where relevant;
- accepted tasks/projects survive Redis loss/restart;
- every action carries actor/capability/request ID;
- context pruning preserves reconstructability;
- agent/source changes are benchmarked before promotion;
- costs, latency, adapter health and failures are visible.

---

# 8. What Not to Build Yet

Until the vertical slice passes:

- broad autonomous submission;
- all 50 state adapters;
- nationwide uncontrolled foundation crawling;
- giant generalized knowledge graph;
- complicated multi-model fleet;
- Kubernetes;
- dozens of long-lived specialist agents;
- autonomous production code/policy self-modification;
- Phase 2 outreach execution;
- full Phase 3 tracker;
- custom vector database;
- permanent memory for every worker;
- expensive Candid dependency before free-source coverage is measured.

Architect extension points now; earn complexity later.

---

# 9. R0 → G0 Handoff

R0 now recommends G0 ratify these laws:

1. **Hermes operates; the platform owns truth.**
2. **Personal cognition and operational cognition stay separate.**
3. **Workers are bounded/disposable; traces are sidechains, not parent memory.**
4. **Deterministic constraints decide deterministic questions.**
5. **Every promoted claim, memory, action and agent change requires lineage/evidence.**
6. **Every external fact enters through a registered source and immutable snapshot.**
7. **Source authority and freshness are fact-specific and executable.**
8. **Material source revisions invalidate/re-evaluate dependent decisions.**
9. **Internal grant models should interoperate with CommonGrants rather than creating an isolated private schema.**
10. **The first vertical slice proves the system against real official grant data.**

With these laws, the product can reuse substantial Larger Lab/OCE/Hermes infrastructure while building the true competitive layer around Grant domain intelligence, evidence, eligibility, matching and application production.