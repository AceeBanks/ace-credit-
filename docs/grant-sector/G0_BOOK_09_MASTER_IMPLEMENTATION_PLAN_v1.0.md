# G0 Book 9 — Runtime Substrate ADR, Clean Production Repository & G1 Handoff Master Implementation Plan

**Document ID:** GS-G0-B9-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR EXECUTION AFTER BOOK 8 RATIFICATION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Receives from:** Books 0–8 + Amendments 001–002  
**Produces:** Ratified production architecture seed + G1 implementation backlog

---

# 0. Book Mission

Book 9 is the final G0 planning/foundation book.

Its job is to convert all prior constitutional, domain, data, cognition, evidence, security, evaluation, and integration contracts into a **single production implementation baseline**.

The governing question is:

> **What exact runtime, repository structure, service topology, dependency set, deployment model, operational controls, and implementation backlog should we build so that Books 1–8 remain true in production with the least unnecessary custom infrastructure?**

Book 9 does not redesign the Grant machine.

It selects and freezes the machinery underneath it.

The key principle is:

> **Choose the substrate that removes the most generic runtime engineering while changing the least product architecture.**

---

# 1. What Book 9 Must Not Become

Book 9 is NOT:

- a generic “agent OS” selection contest;
- a rewrite of the Dual-Hermes architecture;
- a chance to replace the Grant domain with framework objects;
- permission to loosen tenant/security boundaries for convenience;
- an excuse to merge prototype code blindly into production;
- a cloud-infrastructure shopping exercise disconnected from workload evidence;
- a feature expansion phase;
- a submission-automation phase.

Book 9 freezes production implementation choices only after Books 0–8 have defined and tested what the product requires.

---

# 2. Hard Inputs from Previous Books

Book 9 treats the following as constitutional constraints:

1. Personal Hermes and CEO Hermes remain distinct actors.
2. Hermes is an operator, not canonical truth.
3. Workers remain task-scoped and non-sovereign.
4. Postgres/domain state remains canonical unless an explicitly ratified Book 9 ADR proves an equivalent durable system of record without semantic loss.
5. Redis/queues/cache are never sovereign truth.
6. Book 2 domain identity remains provider-independent.
7. Book 3 SourceSnapshot/provenance semantics remain immutable.
8. Book 5 decision/evidence replay remains possible.
9. Book 6 authority is deny-by-default and independent of tool availability.
10. Secrets remain outside agent context.
11. External submission remains disabled in G0 / initial Phase 1.
12. Book 7 promotion/evaluation governs behavioral changes.
13. Book 8 vertical slice is the reference workload.
14. External frameworks must be replaceable and pass exit/rebuild tests.
15. No runtime may create a second policy, memory, workflow, evidence, identity, or tenant authority.

If a runtime candidate cannot satisfy these, it is disqualified regardless of developer convenience.

---

# 3. Book Theme

## Measure → Compare → Decide → Seed → Verify → Handoff

```text
BOOK 8 MEASURED WORKLOAD
        ↓
RUNTIME REQUIREMENTS MATRIX
        ↓
OCE/native vs Compozy vs QM vs bounded hybrid
        ↓
HARD-GATE ELIMINATION
        ↓
WEIGHTED COMPARISON
        ↓
RUNTIME SUBSTRATE ADR
        ↓
PRODUCTION SERVICE TOPOLOGY
        ↓
CLEAN REPOSITORY SEED
        ↓
CI / ENVIRONMENTS / OPERATIONS
        ↓
SEED VERIFICATION
        ↓
G1 BUILD BACKLOG
        ↓
G0 FINAL REALITY LOCK
```

---

# 4. Required Artifact Set

```text
docs/grant-sector/g0/09-production-seed/
├── G0_B9_RUNTIME_REQUIREMENTS_MATRIX.md
├── G0_B9_BOOK8_WORKLOAD_EVIDENCE.md
├── G0_B9_RUNTIME_CANDIDATE_PROFILES.md
├── G0_B9_RUNTIME_BAKEOFF_PLAN.md
├── G0_B9_RUNTIME_BAKEOFF_RESULTS.md
├── G0_B9_RUNTIME_SUBSTRATE_ADR.md
├── G0_B9_PRODUCTION_SERVICE_TOPOLOGY.md
├── G0_B9_CANONICAL_STATE_OWNERSHIP.md
├── G0_B9_DEPENDENCY_MANIFEST.md
├── G0_B9_LICENSE_RISK_REGISTER.md
├── G0_B9_REPOSITORY_STRUCTURE.md
├── G0_B9_MODULE_OWNERSHIP_MAP.md
├── G0_B9_API_CONTRACT_MAP.md
├── G0_B9_ENVIRONMENT_STRATEGY.md
├── G0_B9_LOCAL_DEV_STRATEGY.md
├── G0_B9_DEPLOYMENT_STRATEGY.md
├── G0_B9_DATA_MIGRATION_SEED.md
├── G0_B9_CI_CD_POLICY.md
├── G0_B9_OBSERVABILITY_SLO_BASELINE.md
├── G0_B9_BACKUP_RECOVERY_PLAN.md
├── G0_B9_SECURITY_BASELINE.md
├── G0_B9_SECRET_MANAGEMENT_PLAN.md
├── G0_B9_COST_ENVELOPE.md
├── G0_B9_G1_IMPLEMENTATION_BACKLOG.md
├── G0_B9_SEED_VERIFICATION_REPORT.md
├── G0_B9_FINAL_G0_RATIFICATION_PACKET.md
└── G0_B9_REALITY_LOCK_REPORT.md
```

Machine-readable companion artifacts are required for candidate scores, dependency pins, service ownership, environment config, seed manifest, G1 backlog, and Reality Lock.

---

# 5. Chapter B9.C1 — Book 8 Workload Evidence Intake

## Objective

Make runtime selection evidence-driven.

Extract measured Book 8 workload characteristics:

- number of concurrent client/application projects;
- average/peak worker fanout;
- average TaskContract duration;
- long-running/background jobs;
- source fetch volume;
- parser workload;
- context size distribution;
- sidechain volume;
- retry/recovery needs;
- audit events per run;
- evidence/graph operations;
- artifact generation size/frequency;
- DB transaction patterns;
- queue/event patterns;
- model calls and fallback patterns;
- restart/reconstruction time;
- approval interactions;
- cost/latency measurements;
- tenant isolation requirements.

Book 8 observations become the benchmark rather than guessed enterprise requirements.

## Deliverable

`G0_B9_BOOK8_WORKLOAD_EVIDENCE.md`

## Gate

No substrate scoring before workload evidence is captured.

---

# 6. Chapter B9.C2 — Production Runtime Requirements Matrix

Translate Books 1–8 into implementation requirements.

Required categories:

### Identity / scope

- user identity;
- service identity;
- Personal Hermes identity;
- CEO Hermes identity;
- worker identity;
- tenant/project/resource scope.

### Durable execution

- task persistence;
- checkpoint/resume;
- restart recovery;
- bounded retries;
- background jobs;
- idempotency.

### Agent execution

- Hermes adapter;
- worker sandbox;
- context injection;
- sidechain storage;
- structured result return;
- typed agent messages.

### Policy/tool control

- capability registry;
- deny-by-default authorization;
- credential injection;
- tool allowlist;
- egress control;
- approvals.

### Data/evidence

- canonical Postgres ownership;
- immutable source snapshots;
- artifacts/object storage;
- provenance refs;
- evidence/graph projection compatibility.

### Evaluation

- shadow runs;
- candidate versioning;
- rollback;
- eval fixture execution.

### Operations

- observability;
- tracing;
- metrics;
- backup/recovery;
- local development;
- cloud deployment;
- cost control.

Every requirement classifies:

```yaml
requirement_id:
source_book:
hard_gate: true|false
priority: P0|P1|P2
book8_evidence_ref:
acceptance_test:
```

Commit: `G0-B9-C1-C2: freeze production workload and runtime requirements`

---

# 7. Chapter B9.C3 — Runtime Candidate Profiles

Formal candidates:

### Candidate A — OCE-native / project-owned runtime

Reuse selected Larger-Lab/OCE/Hermes infrastructure under our contracts.

### Candidate B — CompozyOS substrate

Use Compozy for bounded durable execution/session/task/capability mechanics while preserving project-owned domain/policy/evidence semantics.

### Candidate C — QM substrate

Use QM for bounded runtime/sandbox/scope/session mechanics while preserving project-owned semantics.

### Candidate D — Bounded hybrid

Use a narrow external runtime component where it reduces complexity without surrendering control.

## Profile fields

```text
version/commit
license
maturity
language/runtime
storage model
session model
task model
worker model
permissions
approvals
MCP/tool model
credential handling
multi-tenancy
observability
failure/recovery
local dev
cloud path
extension/plugin model
exportability
known constraints
custom glue required
```

No candidate receives credit for features irrelevant to the Grant machine.

---

# 8. Chapter B9.C4 — Hard-Gate Elimination

Before weighted scoring, run constitutional hard gates.

A candidate is disqualified if it cannot prove:

1. Personal/CEO identity separation;
2. tenant/project isolation;
3. task-scoped worker authority;
4. deny-by-default capability enforcement;
5. external-action separation from drafting;
6. server-side secret handling;
7. canonical Grant/domain state independence;
8. SourceSnapshot/evidence identity preservation;
9. audit/provenance ID compatibility;
10. durable accepted-task recovery;
11. restart/reconstruction;
12. export/rebuild/exit path;
13. no shared cross-user “mind” state;
14. no framework-owned invisible self-modification;
15. submission remains disabled.

Disqualified candidates do not continue merely because they score well elsewhere.

---

# 9. Chapter B9.C5 — Runtime Bake-Off

Use Book 8 workloads against surviving candidates.

Test workloads:

### W1 — Personal→CEO intent handoff

### W2 — bounded worker fanout

### W3 — long research task + checkpoint/resume

### W4 — worker failure/retry

### W5 — process/runtime restart mid-application

### W6 — scoped background source refresh

### W7 — approval-gated operation

### W8 — credential-injected external API call

### W9 — malicious tool/prompt attempt

### W10 — multi-project concurrency

### W11 — multi-tenant isolation

### W12 — audit/evidence linkage

### W13 — shadow evaluation run

### W14 — artifact/object handling

### W15 — runtime export/exit

Metrics:

- correctness;
- Book 1–8 contract fit;
- code/glue required;
- operational complexity;
- p50/p95 latency;
- restart recovery;
- observability;
- testability;
- resource footprint;
- deployment complexity;
- upgrade risk;
- developer ergonomics;
- exit cost.

---

# 10. Chapter B9.C6 — Weighted Runtime Decision

Suggested weights:

```text
Constitutional / contract fit          20%
Tenant + security enforcement          15%
Durable execution / recovery           12%
Dual-Hermes / worker fit               10%
Canonical-state independence           10%
Audit / replay compatibility            8%
Operational simplicity                  7%
Custom glue eliminated                  5%
Observability                            4%
Performance                              3%
Local/cloud deployment                   2%
License / upstream risk                  2%
Exit / rebuild cost                      2%
```

Hard gates override weights.

## Decision objective

Select the smallest runtime surface that removes substantial generic engineering while preserving project sovereignty.

## Required outcome

`G0_B9_RUNTIME_SUBSTRATE_ADR.md`

Status must be one of:

- OCE_NATIVE;
- COMPOZY_BOUNDED;
- QM_BOUNDED;
- HYBRID_BOUNDED.

No `TBD` at Book 9 completion.

Commit: `G0-B9-C3-C6: complete runtime bake-off and ratify substrate ADR`

---

# 11. Chapter B9.C7 — Canonical State Ownership Matrix

Freeze who owns what.

Example target:

```text
Postgres
- Organization
- Opportunity/Application domain state
- authoritative workflow state
- capability/policy data
- approvals
- DecisionRecords
- audit indexes

Object Storage
- raw SourceSnapshots
- uploaded documents
- generated artifacts
- immutable large evidence payloads

Redis / queue
- ephemeral transport
- cache
- leases
- rate limits
- non-authoritative work signaling

Graph/Semantica projection (if selected)
- rebuildable evidence/relationship traversal

Vector index
- rebuildable semantic retrieval

Hermes memory
- curated non-authoritative Personal/CEO continuity only
```

No ambiguous dual ownership.

---

# 12. Chapter B9.C8 — Production Service Topology

Freeze the smallest service architecture that satisfies Books 1–8.

Candidate logical services:

- API / app backend;
- Personal Hermes service/adapter;
- CEO Hermes service/adapter;
- worker execution service;
- policy/capability service;
- source ingestion service;
- evidence/research service;
- application/drafting service;
- artifact service;
- evaluation service;
- tool gateway;
- scheduler/background jobs;
- Postgres;
- Redis/queue if justified;
- object storage;
- optional graph/vector projection.

Do not split into microservices merely to appear enterprise-grade.

Rule:

> Start modular-monolith or few-service where operationally simpler; preserve internal module boundaries so extraction later is possible.

Every service/module gets:

- owner;
- data ownership;
- input/output contracts;
- failure mode;
- auth boundary;
- observability;
- scaling trigger.

---

# 13. Chapter B9.C9 — API / Event Contract Map

Freeze the top-level interfaces connecting modules.

Examples:

```text
POST /intent
POST /opportunities/search
POST /eligibility/evaluate
POST /applications
POST /applications/{id}/draft
POST /qa/run
POST /artifacts/generate
POST /approvals
```

Internal messages/events:

```text
IntentAccepted
TaskAccepted
TaskCompleted
SourceSnapshotCreated
OpportunityRevisionCreated
EligibilityInvalidated
ApplicationDrafted
QACompleted
ApprovalRequired
ArtifactVersionCreated
CandidateChangeProposed
```

Exact API shape may evolve in G1, but ownership and semantic event boundaries must be frozen.

---

# 14. Chapter B9.C10 — Clean Repository Structure

Create the clean production repository only after runtime ADR.

Recommended structure:

```text
apps/
  api/
  web/

platform/
  auth/
  policy/
  runtime/
  tools/
  evidence/
  evaluation/
  artifacts/
  observability/

agents/
  personal_hermes/
  ceo_hermes/
  workers/
  contracts/

sectors/
  grants/
    domain/
    sources/
    matching/
    eligibility/
    applications/
    research/
    budgets/
    qa/

schemas/
config/
migrations/
tests/
evals/
infra/
docs/
```

The final layout should follow language/framework conventions while preserving the same ownership boundaries.

## Hard rule

Do not transplant trading-domain directories into the clean repository.

---

# 15. Chapter B9.C11 — Seed Manifest

Every file/component entering the clean repo must have lineage:

```yaml
seed_item_id:
destination:
source_type: NEW|SALVAGED|EXTERNAL_WRAPPED
source_repo:
source_path:
source_commit:
license:
modifications:
owner_module:
reason:
tests_required:
```

This prevents archive pollution and mystery copied code.

---

# 16. Chapter B9.C12 — Dependency & License Freeze

Pin major dependencies by version/commit.

For each:

- purpose;
- license;
- optional/required;
- transitive risk;
- security maintenance;
- replacement path;
- feature subset actually used.

Review all external candidates selected through earlier books, including any chosen runtime, parser, eval, document, or integration library.

No dependency simply because it was in a prototype.

---

# 17. Chapter B9.C13 — Initial Database / Migration Seed

Translate Books 2–6 contracts into initial migration ownership.

Do not attempt full G1 feature schema in G0, but seed:

- tenants/users/memberships;
- actor/service identities;
- capability/policy metadata;
- organizations;
- grant opportunities/revisions;
- ApplicationProject shell;
- SourceRegistry/Snapshot metadata;
- audit/DecisionRecord foundations;
- artifact metadata;
- task/run foundations if runtime does not own them externally.

Migration tests must run from empty DB and support rollback strategy appropriate to chosen migration framework.

---

# 18. Chapter B9.C14 — Environment Strategy

Define environments:

### LOCAL

Developer laptop, no paid cloud required for core development.

### TEST/CI

Ephemeral/reproducible.

### STAGING

Production-like with synthetic/test tenant data.

### PRODUCTION

Real tenant data.

Rules:

- configs separated from secrets;
- same schemas/contracts across environments;
- migrations tested before production;
- production credentials unavailable locally by default;
- destructive operations gated.

---

# 19. Chapter B9.C15 — Local Development Experience

One-command or minimal-command setup target.

Provide:

- env bootstrap;
- Postgres;
- Redis only if chosen;
- local object store or filesystem-compatible abstraction;
- runtime daemon if chosen;
- mock/test model configuration;
- deterministic fixture mode;
- seed data;
- health checks.

Developer should be able to run a representative mock application workflow locally.

---

# 20. Chapter B9.C16 — Deployment Strategy

Do not prematurely choose Kubernetes unless Book 8 evidence requires it.

Initial preferred shape:

- containerized services;
- managed Postgres or self-hosted equivalent with proven backup;
- managed/simple object storage;
- lightweight runtime deployment;
- horizontal worker scaling only where measured.

Define:

- regions;
- network boundaries;
- TLS;
- database connectivity;
- worker execution isolation;
- secret injection;
- rolling deployments;
- migration ordering;
- rollback.

Cloud provider selection may remain deployment-configurable if the architecture does not require one vendor.

---

# 21. Chapter B9.C17 — CI / CD Policy

Required CI gates:

```text
format/lint
unit tests
schema tests
domain invariants
policy/security tests
migration tests
provenance tests
eval smoke tests
secret scanning
dependency/license checks
build/container checks
```

For protected production deployment:

- branch protection;
- reviewed changes;
- environment approval where appropriate;
- immutable build artifact;
- migration preview;
- release version/tag;
- rollback reference.

Book 7 promotion is separate from code deployment but must integrate cleanly with it.

---

# 22. Chapter B9.C18 — Observability Baseline

Define metrics/logs/traces from Book 8 measurements.

Minimum:

### Application/runtime

- request/task counts;
- success/failure;
- retries;
- queue depth if relevant;
- task age;
- checkpoint recovery.

### Agent

- model calls;
- tokens;
- latency;
- cost;
- structured-output failures;
- context size;
- worker fanout.

### Data/source

- adapter health;
- snapshot freshness;
- parser failures;
- revision changes.

### Quality

- unsupported claim rate;
- QA failure rate;
- eval regression;
- human edit burden where available.

### Security

- denied capabilities;
- approval requests;
- suspicious egress;
- auth failures;
- cross-tenant attempts.

Structured correlation IDs must connect user request → intent → task → worker → decision → artifact → audit.

---

# 23. Chapter B9.C19 — SLO Baseline

Do not invent unrealistic enterprise SLOs.

Use Book 8 measurements to define initial targets for:

- API availability;
- accepted-task durability;
- task recovery;
- source adapter freshness;
- critical audit write success;
- artifact generation success;
- authorization service availability;
- backup recovery objectives.

Integrity-sensitive properties may have stronger requirements than latency.

Example:

> Better to reject a write than create an unaudited consequential state.

---

# 24. Chapter B9.C20 — Backup / Recovery / Disaster Recovery

Define backup classes:

- canonical database;
- object/artifact storage;
- configuration/policy;
- audit evidence;
- optional graph/vector indexes.

Test:

- DB restore;
- artifact restore;
- runtime restart;
- graph/vector rebuild;
- Hermes reset/reconstruction;
- recovery to a known migration version.

Graph/vector/runtime caches must be rebuildable where constitution says non-sovereign.

---

# 25. Chapter B9.C21 — Secret Management Production Plan

Freeze:

- secret store choice/interface;
- environment injection;
- workload identity;
- credential rotation;
- provider/API credential ownership;
- local dev dummy credentials;
- audit redaction;
- incident revocation path.

No secrets in repo, fixtures, agent memory or normal application logs.

---

# 26. Chapter B9.C22 — Security Baseline Verification

Re-run Book 6 hard boundaries against selected runtime/topology:

- tenant isolation;
- task scope;
- Personal/CEO separation;
- secret brokerage;
- egress;
- prompt injection containment;
- tool-gateway enforcement;
- approvals;
- audit;
- submission disablement.

A runtime ADR is invalid if real integration weakens Book 6 compared with the prototype.

---

# 27. Chapter B9.C23 — Cost Envelope

Use measured Book 8 runtime to estimate:

- model usage;
- source/API costs;
- parser/OCR compute;
- database;
- object storage;
- runtime workers;
- observability;
- optional paid source services.

Provide scenarios:

```text
DEV / SINGLE CLIENT
10 CLIENTS
100 CLIENTS
```

Do not pretend projections are precise. State assumptions and dominant cost drivers.

Use cost only as optimization after correctness/security floors.

---

# 28. Chapter B9.C24 — Clean Repository Seed Creation

Create clean production repository/branch after all prior Book 9 decisions.

Seed only:

- ratified contracts;
- chosen generic infrastructure;
- essential schemas/config;
- initial migrations;
- CI;
- environment tooling;
- tests;
- documentation;
- G1 scaffolding.

Do not import experimental bake-off code unless selected.

Do not import rejected/deferred external projects.

Do not import trading baggage.

---

# 29. Chapter B9.C25 — Seed Verification

Fresh clone test:

```text
clone
→ bootstrap
→ validate configs
→ start local dependencies
→ migrate DB
→ load fixtures
→ run core tests
→ run policy tests
→ run minimal mock Grant workflow
```

Verification must prove no dependence on developer machine state, old branch paths, hidden environment variables, or archived Hermes memory.

---

# 30. Chapter B9.C26 — G1 Implementation Backlog

Translate Book 8 vertical slice into actual build order.

Recommended G1 epics:

### G1.1 Platform kernel

Identity, tenants, policy, task/run foundations.

### G1.2 Grant domain persistence

Organization, opportunity/revision, application project.

### G1.3 Source ingestion

Grants.gov/Simpler + Georgia-first adapter + SourceSnapshot.

### G1.4 Eligibility and matching

Candidate rule extraction + validation + deterministic evaluation + ranking.

### G1.5 Research/evidence

USAspending/winner/community evidence + evidence lineage.

### G1.6 Personal/CEO Hermes

IntentContract, TaskContract, context assembly, workers.

### G1.7 Application drafting

Blueprint, requirements, proposal/business-plan/budget artifacts.

### G1.8 QA/evaluation

Claim ledger, factuality, Book 7 gates.

### G1.9 Client-facing app

Intake, grant shortlist, research visibility, draft review.

### G1.10 Operations hardening

Monitoring, recovery, cost, scaling, security verification.

Each epic decomposes into chapter-sized work packets with acceptance tests derived from G0—not new architecture discussions.

---

# 31. Chapter B9.C27 — G1 Priority Rules

Priority order:

1. correctness foundations;
2. client-visible vertical slice;
3. reliability/security;
4. throughput/cost optimization;
5. secondary integrations;
6. later automation.

Do not prioritize:

- exotic multi-agent behaviors;
- autonomous self-modification;
- huge plugin ecosystems;
- 50-state coverage before demand;
- automatic grant submission;
- speculative scale infrastructure.

The client should gain usable Grant discovery + drafting capability as early as the core contracts safely allow.

---

# 32. Chapter B9.C28 — Architecture Decision Freeze

Create final G0 ADR index.

Every material decision gets status:

- RATIFIED;
- PROVISIONAL_G1_VALIDATE;
- DEFERRED;
- REJECTED.

No unresolved P0 `TBD` items.

Examples to freeze:

- runtime substrate;
- canonical DB;
- queue/Redis role;
- object storage abstraction;
- graph/evidence substrate;
- vector retrieval approach;
- parser choices;
- evaluation tooling;
- identity/auth approach;
- tool gateway;
- deployment topology;
- clean repo structure.

---

# 33. Chapter B9.C29 — Final G0 Contradiction Sweep

Re-run contradictions across Books 0–9 and amendments.

Classes:

- authority;
- identity;
- storage ownership;
- runtime ownership;
- workflow;
- memory;
- evidence;
- security;
- deployment;
- evaluation;
- client scope;
- terminology.

Any P0 inconsistency blocks completion.

Book 9 must ensure its implementation choices do not silently invalidate earlier constitutional claims.

---

# 34. Chapter B9.C30 — G0 Final Reconstruction Test

A new engineering team, with only repository artifacts and no conversation history, should be able to determine:

- product mission;
- client Phase 1 scope;
- Personal/CEO responsibilities;
- domain model;
- source/evidence rules;
- security model;
- evaluation/promotion model;
- chosen runtime;
- service topology;
- data ownership;
- deployment approach;
- G1 build sequence;
- why alternatives were rejected.

If undocumented tribal knowledge is required, G0 is not complete.

---

# 35. Chapter B9.C31 — Final G0 Reality Lock

Required machine-readable result:

```json
{
  "phase": "G0",
  "status": "PASS|FAIL",
  "books_ratified": 10,
  "p0_open": 0,
  "runtime_substrate_selected": true,
  "runtime_hard_gates_pass": true,
  "canonical_ownership_frozen": true,
  "service_topology_frozen": true,
  "dependency_manifest_complete": true,
  "license_review_pass": true,
  "clean_repo_seeded": true,
  "fresh_clone_bootstrap_pass": true,
  "migration_seed_pass": true,
  "security_baseline_pass": true,
  "recovery_test_pass": true,
  "observability_baseline_defined": true,
  "g1_backlog_complete": true,
  "cross_book_contradiction_pass": true,
  "submission_enabled": false,
  "ready_for_g1": true
}
```

`ready_for_g1` is evidence-derived and may not be hard-coded.

---

# 36. Parallel-Agent Work Allocation

## Lane A — Runtime Evidence

C1–C6.

Owns workload intake, requirements, candidate profiles, hard gates, bake-off, ADR.

Must land first.

## Lane B — Production Architecture

After runtime ADR:

C7–C10.

State ownership, service topology, interfaces, repo structure.

## Lane C — Dependencies / Data Seed

C11–C13.

Seed manifest, dependency/license, migrations.

## Lane D — Environments / Deployment

C14–C17.

Local/staging/prod, deployment, CI/CD.

## Lane E — Operations

C18–C23.

Observability, SLO, recovery, secrets, security, cost.

## Lane F — Clean Seed

C24–C25.

Fresh production repo + reproducibility.

## Lane G — G1 / Final Lock

C26–C31.

Backlog, freeze, contradiction sweep, reconstruction, Reality Lock.

### Merge law

No lane may choose its own runtime or storage authority after C6 ADR.

---

# 37. Commit Plan

```text
1. G0-B9-C1-C2
   workload evidence + production runtime requirements

2. G0-B9-C3-C4
   runtime candidate profiles + hard gates

3. G0-B9-C5
   runtime bake-off results

4. G0-B9-C6
   runtime substrate ADR

5. G0-B9-C7-C10
   state ownership + topology + APIs + repo structure

6. G0-B9-C11-C13
   seed manifest + dependency/license + migration seed

7. G0-B9-C14-C17
   environments + local dev + deployment + CI/CD

8. G0-B9-C18-C23
   observability + SLO + recovery + secrets + security + cost

9. G0-B9-C24-C25
   clean repository seed + fresh clone verification

10. G0-B9-C26-C28
    G1 backlog + priority + architecture freeze

11. G0-B9-C29-C30
    contradiction sweep + reconstruction test

12. G0-B9-BOOK
    complete Book 9 implementation checkpoint

13. G0-B9-REPAIR-01...N
    independent review repairs

14. G0-B9-RATIFY
    Book 9 Reality Lock PASS

15. G0-RATIFY
    Final G0 Reality Lock / handoff to G1
```

---

# 38. Allowed / Prohibited Work

## Allowed

- runtime bake-off prototypes;
- production topology/docs;
- clean repository seed;
- initial migrations;
- CI/environment/bootstrap;
- chosen adapters/wrappers;
- operational baselines;
- G1 backlog.

## Prohibited

- adding new product features not required by Books 1–8;
- automatic grant submission;
- rebuilding constitutional/domain contracts for runtime convenience;
- importing every external candidate;
- speculative Kubernetes/service mesh complexity;
- shared Personal/CEO memory;
- framework-owned canonical Grant state;
- production self-modification;
- trading code migration.

---

# 39. Definition of Done

Book 9 is complete only when:

1. Book 8 workload evidence is summarized;
2. production requirements derive from Books 1–8;
3. all runtime candidates are profiled against same requirements;
4. hard-gate failures eliminate candidates;
5. bake-off results are recorded;
6. one runtime substrate ADR is ratified;
7. canonical data ownership is frozen;
8. production service/module topology is frozen;
9. interfaces/events are mapped;
10. clean repo structure is defined;
11. seed manifest has source/license lineage;
12. dependencies are pinned/reviewed;
13. initial migrations work;
14. local/test/staging/prod strategy exists;
15. fresh local bootstrap works;
16. deployment strategy is reproducible;
17. CI/CD enforces required gates;
18. observability/SLO baseline exists;
19. backup/recovery is tested;
20. secret/security baseline passes;
21. cost envelope exists;
22. clean production seed exists;
23. fresh clone verification passes;
24. G1 backlog maps directly to ratified contracts;
25. no unresolved P0 architecture contradiction remains;
26. new engineering team can reconstruct architecture from repo alone;
27. G0 final Reality Lock outputs `ready_for_g1=true`.

---

# 40. Book 9 North-Star Test

At the end of Book 9, ask a new senior engineer:

> “Build the production Grant platform.”

They should not need to ask:

```text
Which agent owns client conversation?
Which agent runs operations?
Where does truth live?
What runtime are we using?
Can workers call any tool?
How are credentials handled?
What does an OpportunityRevision mean?
How are grants sourced?
What counts as evidence?
How is eligibility evaluated?
How are decisions replayed?
How are behavior changes promoted?
What gets deployed?
What do I build first?
```

Those answers must already exist in ratified repository artifacts.

The remaining questions should be ordinary implementation questions—not foundational architecture questions.

If Book 9 leaves the engineering team debating what the product fundamentally is, G0 has failed.

If Book 9 leaves them with a clean repo, frozen contracts, chosen runtime, reproducible environment, measured workload, and a chapter-sized G1 backlog, G0 is complete.