# R0 Seed Architecture Recommendation

**Document ID:** GS-R0-SEED-001  
**Version:** 0.1  
**Status:** RECOMMENDED INPUT TO G0  
**Date:** 2026-08-24

---

## 0. Decision

Do not seed the future Grant Sector repository from any one existing branch.

Create a clean repository after G0 ratifies the contracts, then transplant selected proven components behind new product interfaces.

The future product should be architected as a **domain-neutral governed platform kernel + Grant Sector module + two Hermes operator profiles**.

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
│  Identity / Tenant / Policy / Audit / Event / Project State │
│                          │                                   │
│                CEO HERMES PROFILE                            │
│               planner + application operator                 │
│                          │                                   │
│         pre-tool policy → execute → post-tool verify         │
└─────────────────────────┬────────────────────────────────────┘
                          │ Task Contracts
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                       WORKER FABRIC                          │
│                                                              │
│ Research  Parser  Evidence  Proposal  QA  Artifact workers  │
│                                                              │
│ Short result → CEO                                          │
│ Full trace → sidechain / audit storage                       │
└─────────────────────────┬────────────────────────────────────┘
                          │
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
│ PostgreSQL authoritative state                              │
│ Object storage: uploads/source snapshots/generated files     │
│ Redis optional transport/cache only                          │
│ Vector retrieval attached to canonical identities            │
│ Observability / audit / backup / restore                      │
└──────────────────────────────────────────────────────────────┘
```

---

# 2. Salvaged Seed Packages

## Package A — Hermes Operator Gateway

Source:

- `hermes-set-up/oce-hermes-telegram-operator`

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

Change:

- rename OCE observer tools into product capabilities;
- support separate Personal and CEO profiles;
- preserve read-only-by-default posture;
- add explicit authority tiers and tenant/project scoping;
- no direct DB access from Hermes.

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
- parser/semantic/graph contracts.

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

- source clients;
- Postgres persistence;
- grant evidence evaluator;
- model routing;
- exact research-agent roles.

## Package D — Agent Governance Harness

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
- task/project checkpoints.

## Package E — Agent Evaluation Lab

Source:

- archived Hermes `skill-creator`.

Generalize:

```text
candidate skill/prompt/workflow
        ↓
versioned eval corpus
        ↓
parallel candidate + baseline
        ↓
formal assertions + human review
        ↓
quality / latency / tokens / cost
        ↓
variance + regression analysis
        ↓
PROMOTE | REVISE | REJECT
```

Use for every important agent role and for Personal→CEO handoff quality.

## Package F — Document / Artifact Ingestion

Sources:

- Parser Router architecture;
- MarkItDown / ODL-PDF / Chandra / optional LiteParse.

Build a stable `SourceDocument` adapter contract. Treat parser engines as replaceable workers.

## Package G — Client Artifact Output

Sources:

- Open Design;
- D2;
- web artifact builder where useful.

Use selectively for visual outputs and internal review. Build a separate canonical application/document compiler so visual tooling never owns facts.

---

# 3. New Product Packages

These should be written specifically for the Grant domain rather than ported.

```text
sectors/grants/domain/
    organization.py
    opportunity.py
    funder.py
    award.py
    eligibility.py
    application.py
    requirement.py
    budget.py
    outcome.py

sectors/grants/sources/
    adapters/
    normalization/
    revisions/

sectors/grants/matching/
    eligibility_engine/
    ranking/
    explanations/

sectors/grants/research/
    funder/
    winner/
    community_impact/

sectors/grants/evidence/
    claims/
    sources/
    lineage/
    contradictions/

sectors/grants/application_factory/
    blueprint/
    sections/
    facts/
    compiler/

sectors/grants/qa/
    eligibility/
    requirements/
    factuality/
    citations/
    numerical/
    consistency/
    alignment/
    style/
```

---

# 4. Suggested Future Repository Shape

Working name only; final product/repository name is deferred.

```text
repo/
├── apps/
│   ├── web/
│   ├── api/
│   └── worker/
│
├── platform/
│   ├── identity/
│   ├── policy/
│   ├── audit/
│   ├── events/
│   ├── tasks/
│   ├── memory/
│   ├── evidence/
│   ├── artifacts/
│   ├── models/
│   └── observability/
│
├── agents/
│   ├── hermes-personal/
│   ├── hermes-ceo/
│   ├── skills/
│   ├── workers/
│   └── evals/
│
├── sectors/
│   └── grants/
│       ├── domain/
│       ├── sources/
│       ├── eligibility/
│       ├── matching/
│       ├── research/
│       ├── evidence/
│       ├── applications/
│       └── qa/
│
├── schemas/
├── migrations/
├── infra/
├── tests/
├── evals/
└── docs/
```

---

# 5. Core Contracts to Freeze in G0

Before implementation, G0 should define and version at least:

1. `IntentContract`
2. `ClarificationRequest`
3. `TaskContract`
4. `WorkerResult`
5. `OutcomeArtifact`
6. `OrganizationProfile`
7. `GrantOpportunity`
8. `EligibilityRule`
9. `EligibilityDecision`
10. `MatchExplanation`
11. `SourceSnapshot`
12. `EvidenceClaim`
13. `ResearchPack`
14. `ApplicationProject`
15. `CanonicalFact`
16. `BudgetModel`
17. `RequirementChecklist`
18. `ArtifactManifest`
19. `QAReport`
20. `ApprovalDecision`
21. `AgentIdentity`
22. `CapabilityGrant`
23. `AuditEvent`
24. `MemoryCandidate/Promotion`
25. `FeedbackOutcome`

These contracts become the stable seams around which upstream components can be swapped.

---

# 6. Vertical Slice Recommendation

Do not initially build every grant source or every document type.

The first evidence-backed vertical slice should prove the architecture end-to-end:

```text
Client idea / request
   ↓
Personal Hermes clarification
   ↓
Intent Contract
   ↓
CEO Hermes plan
   ↓
One real grant source adapter
   ↓
Opportunity normalization
   ↓
Deterministic eligibility
   ↓
Research workers
   ↓
Evidence Graph
   ↓
Explainable match
   ↓
One proposal blueprint + selected sections
   ↓
QA
   ↓
Human review
   ↓
Client-facing result through Personal Hermes
```

Required proof:

- no raw chat polluted into worker prompts unnecessarily;
- no worker transcript pollutes CEO active context;
- every material claim has source lineage;
- eligibility result is reproducible;
- system restarts without losing accepted task/project state;
- every action has actor/capability/request ID;
- context pruning does not lose reconstructability;
- candidate/baseline evals can quantify agent changes;
- cost/latency/error metrics are visible.

---

# 7. What Not to Build Yet

Until the vertical slice passes:

- broad autonomous submission;
- giant generalized knowledge graph;
- complicated multi-model routing fleet;
- Kubernetes;
- dozens of specialist agents;
- autonomous code self-modification;
- Phase 2 outreach execution;
- Phase 3 full tracker UI;
- custom vector database;
- long-term memory for every worker;
- every state/corporate/foundation source.

Architect extension points now; earn complexity later.

---

# 8. R0 → G0 Handoff

R0 recommends that G0 ratify five architectural laws:

1. **Hermes operates; the platform owns truth.**
2. **Personal cognition and operational cognition stay separate.**
3. **Workers are bounded and disposable; traces are sidechains, not parent memory.**
4. **Deterministic constraints decide deterministic questions.**
5. **Every promoted claim, memory, action, and agent change requires lineage and evidence.**

If G0 ratifies these laws, the product can reuse substantial Larger Lab/OCE work without inheriting Larger Lab’s historical complexity.