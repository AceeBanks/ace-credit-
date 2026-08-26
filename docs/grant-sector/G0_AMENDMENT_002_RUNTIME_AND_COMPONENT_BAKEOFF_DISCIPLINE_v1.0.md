# G0 Amendment 002 — Runtime & Component Bake-Off Discipline

**Document ID:** GS-G0-AMD-002  
**Version:** 1.0  
**Status:** ACTIVE PLANNING AMENDMENT — DOES NOT ALTER BOOK 1 CONSTITUTIONAL LAW  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Applies to:** Books 3, 4, 6, 7, 8, and 9  
**Does not reopen:** Books 1–2 constitutional/domain meaning

---

# 0. Purpose

Recent external-repository review produced several potentially useful implementation candidates: Marker, QM, CompozyOS, Headlong, Hermes plugin/evolution projects, Agent-Reach, and related development/runtime tooling.

This amendment integrates only the portions that directly reduce engineering burden or strengthen a contract already required by the Grant Sector architecture.

It deliberately rejects the common failure mode of turning a focused product into a generalized “super-agent” platform merely because external projects expose impressive features.

The governing rule is:

> **Books define what must be true. External components compete only to implement bounded parts of those contracts. No component may redefine the product, the Dual-Hermes design, domain sovereignty, evidence authority, or constitutional control model.**

---

# 1. Constitutional Non-Dilution Rules

This amendment is subordinate to Book 1 and preserves the following invariants without modification:

1. Personal Hermes and CEO Hermes remain distinct actors.
2. Hermes operates the product; Hermes is not the product or source of truth.
3. Workers remain bounded, task-scoped and non-sovereign.
4. Canonical state remains outside agent memory.
5. Tool availability does not grant authority.
6. Deterministic constraints remain deterministic.
7. External facts require governed evidence lineage.
8. Cross-tenant leakage remains P0.
9. Secrets remain outside conversational/agent memory.
10. External submission remains disabled during Phase 1.
11. Safe grant research and drafting remain early L2 capabilities.
12. External frameworks may not create a second workflow, memory, policy, evidence, or identity authority.
13. Optional infrastructure must be replaceable and pass an exit/rebuild test.
14. The product optimizes for high-quality grant intelligence and application production—not generalized autonomy for its own sake.

Any candidate that requires weakening one of these laws is automatically rejected regardless of feature depth.

---

# 2. Component Disposition Summary

| Candidate | Disposition | Allowed role | Explicitly prohibited role |
|---|---|---|---|
| Marker | P0 parser bake-off | document extraction engine behind SourceDocument contract | source/provenance authority |
| Agent-Reach | P1 bounded research adapter | secondary/public-source discovery and research | primary grant truth / policy authority |
| QM | P0 architecture/runtime comparison | scoped sessions, sandbox, policy/runtime patterns | replace Product Constitution or Dual-Hermes semantics |
| CompozyOS | P0 runtime/control-plane comparison | durable execution, sessions, loops, approvals, capabilities, extensions | become sovereign product/control model by default |
| Headlong | pattern/reference | trajectory DAG, compaction, fork-test-merge ideas | shared “one mind” production memory across users/tenants |
| 42-evey Hermes plugins | selective P1 bake-off | telemetry, cost, delegation, session/sandbox helpers | wholesale plugin-suite install or autonomous authority expansion |
| SkillClaw | Book 7 candidate | candidate skill evolution | direct auto-promotion into production skills |
| Hermes Dojo | Book 7 candidate | performance/weakness detection | self-ratifying system changes |
| Hermes Skill Factory | pattern/reference pending license | workflow→candidate skill generation | silent production skill installation |
| Hermes Workspace | P2 internal UI reference | operator/admin console patterns | canonical backend or memory authority |
| Scanopy | DEFER | infrastructure-ops/network documentation later | Grant runtime dependency |
| FrontierAgent / CanvasTTY / OMP | development-tool references | build/operator ergonomics | client Grant runtime authority |

---

# 3. Book 3 Amendment — Document & Research Adapter Bake-Off

## 3.1 Marker inclusion

Book 3 parser/source-ingestion planning shall add **Marker** as a formal extraction-engine candidate.

The product-owned `SourceDocument` / `SourceSnapshot` / provenance contracts remain authoritative.

Marker competes only on extraction capability.

### Parser bake-off lanes

```text
NORMAL DIGITAL PDF / DOCX / HTML
- salvaged MarkItDown
- Unstructured
- Marker

COMPLEX TABLE / FORM / LAYOUT
- Marker
- OpenDataLoader PDF
- Unstructured

SCANNED / OCR-HEAVY
- Marker
- Chandra

VISUAL-LAYOUT FAILURE / NON-TEXTUAL CONTENT
- PixelRAG fallback
```

### Required metrics

- text fidelity;
- heading/section structure;
- table fidelity;
- form-field retention;
- page/locator traceability;
- image/chart preservation metadata;
- scanned-document performance;
- latency;
- CPU/GPU requirements;
- deterministic reproducibility;
- failure detection;
- license/model-weight constraints;
- ability to wrap without leaking engine-specific semantics into canonical domain.

### Hard gate

No parser wins if it cannot preserve or reconstruct enough location metadata to support Book 5 evidence lineage for material claims.

## 3.2 Agent-Reach inclusion

Agent-Reach may be evaluated as a **secondary research-source adapter** for public/social surfaces where it materially improves funder, corporate-grant, organization, or community-context research.

Rules:

- it enters through Book 3 SourceRegistry;
- its content is Tier C/D/E depending source type, never automatically Tier A/B;
- source snapshots and Book 5 evidence rules still apply;
- social/search results are discovery evidence, not final opportunity truth;
- Book 6 egress/credential policy governs access;
- no dependency on Agent-Reach is required for first federal/Georgia vertical slice.

---

# 4. Book 4 Amendment — Runtime Implementation Bake-Off Without Cognitive Redesign

Book 4's Dual-Hermes protocol, memory constitution, `IntentContract`, `TaskContract`, `ContextBundle`, `WorkerResult`, `OutcomeArtifact`, sidechain doctrine and reconstruction rules remain unchanged.

External runtimes may compete only to implement bounded execution mechanics underneath those contracts.

## 4.1 Candidate runtime patterns

Evaluate:

- existing OCE / Larger-Lab runtime patterns;
- native Hermes runtime capabilities;
- QM;
- CompozyOS;
- selected Headlong trajectory/compaction patterns.

## 4.2 Bake-off scope

The comparison is limited to:

- durable session ownership;
- task/run lifecycle;
- worker isolation;
- bounded context injection;
- checkpoint/resume;
- crash/restart recovery;
- background execution;
- structured agent-to-agent messages;
- receipts/results;
- sidechain/trace storage;
- runtime observability;
- workspace/project scope;
- adapterability to our Book 4 schemas.

## 4.3 Explicit exclusions

Do not compare “which framework can make the smartest super-agent.”

Do not adopt:

- shared cross-user thought streams;
- framework-owned permanent Personal/CEO memory semantics;
- framework-defined task contracts replacing ours;
- autonomous worker spawning outside CEO/task policy;
- framework-native self-modification that bypasses Book 7 promotion.

## 4.4 Headlong pattern allowance

Headlong concepts may inform:

- append-only execution trajectory;
- context-as-projection;
- decaying-resolution compaction;
- fork→test→merge/discard improvement workflows.

Its shared-mind/no-hard-user-wall architecture is constitutionally incompatible and must not be ported.

---

# 5. Book 6 Amendment — Control-Plane Candidate Comparison

Book 6 security laws remain authoritative. QM and CompozyOS are implementation candidates only where they can satisfy those laws behind project-owned adapters.

## 5.1 QM evaluation scope

Evaluate QM for:

- scope isolation;
- policy runtime;
- session/workspace ownership;
- sandbox isolation;
- per-scope memory/files/permissions;
- shared-skill grants;
- background work;
- admin/security patterns.

## 5.2 CompozyOS evaluation scope

Evaluate CompozyOS for:

- daemon-owned durable execution state;
- sessions/tasks/loops;
- permissions/approvals;
- capabilities;
- extension trust/lifecycle;
- Hermes/ACP adapter support;
- MCP/native tool exposure;
- workspace boundaries;
- provider-home/credential policies;
- gateway/remote-access boundaries;
- structured network messaging/receipts where relevant.

## 5.3 Control-plane hard gates

Neither candidate may be adopted if it cannot demonstrate:

1. deny-by-default capability behavior;
2. independent tenant/project/resource scope enforcement;
3. Personal-vs-CEO principal separation;
4. task-scoped worker authority;
5. server-side secret handling;
6. external-action separation from internal drafting;
7. durable approval linkage;
8. auditable capability invocation;
9. no direct agent bypass to database or unrestricted tools;
10. safe revocation/expiry;
11. rebuild/exit path;
12. ability to run with our Book 1 capability names and Book 6 authorization semantics rather than replacing them.

## 5.4 Treg / Activepieces relationship

Treg remains an architectural pattern for credential injection/tool registry due licensing constraints.

Activepieces remains a subordinate integration executor.

QM/Compozy evaluation does not expand Activepieces authority or make it canonical workflow state.

---

# 6. Book 7 Amendment — Self-Improvement Candidates Under One Promotion System

Book 7 must not become a collection of competing “self-evolving agent” products.

All external skill/evolution projects are treated as **candidate generators, evaluators, or telemetry providers** beneath one project-owned promotion lifecycle.

## 6.1 Candidate set

Evaluate relevant bounded capabilities from:

- archived Hermes Skill Eval Lab;
- Promptfoo;
- Guardrails where structured validation is useful;
- 42-evey Hermes plugins;
- SkillClaw;
- Hermes Dojo;
- Hermes Skill Factory pattern;
- selected Super-Hermes ideas only if they add measurable value;
- Compozy skill-resource lifecycle if its runtime remains a candidate.

## 6.2 Required single promotion path

```text
OBSERVED WORKFLOW / FAILURE
        ↓
CANDIDATE LESSON
        ↓
CANDIDATE SKILL / PROMPT / ROUTE / CHANGE
        ↓
VERSIONED EVAL CORPUS
        ↓
BASELINE VS CANDIDATE
        ↓
DOMAIN ASSERTIONS
SECURITY TESTS
COST / LATENCY
HUMAN REVIEW
        ↓
PROMOTE | REVISE | REJECT
        ↓
MONITORED ROLLOUT
        ↓
ROLLBACK
```

No external tool may bypass this path by writing directly into production Hermes skill directories or production policy.

## 6.3 Priority external plugin categories

Only prioritize plugins directly supporting our machine:

- telemetry;
- cost guarding;
- delegation quality;
- model-routing resilience;
- session guards;
- sandbox/context hygiene;
- bounded cross-agent bridging;
- goal/open-loop handling.

Do not add plugins merely because they provide extra autonomy, personality, or “meta-reasoning.”

---

# 7. Book 8 Amendment — Optional Research Adapter, No New Control Plane

Book 8's production-shaped vertical slice remains centered on:

- Personal Hermes;
- CEO Hermes;
- real federal/Georgia opportunities;
- deterministic eligibility;
- official/historical award research;
- organization verification;
- community evidence;
- governed drafting;
- QA;
- human review.

Agent-Reach may be included only as an **optional secondary-research lane** if it adds demonstrable grant-relevant evidence.

QM/Compozy do not get separate vertical slices. If one is selected earlier as runtime substrate, Book 8 simply exercises the same ratified product contracts through that substrate.

The vertical slice evaluates the Grant machine, not the framework.

---

# 8. Book 9 Amendment — Runtime Substrate ADR

Book 9 must make one explicit runtime-substrate decision before the clean production repository is finalized.

## 8.1 Candidate patterns

### Candidate A — OCE-native / project-owned control plane

Selected Larger-Lab/OCE/Hermes components assembled under our contracts.

### Candidate B — CompozyOS substrate

Compozy daemon/runtime provides bounded durable execution mechanics while Grant/OCE contracts retain authority.

### Candidate C — QM substrate

QM provides bounded runtime/scope/sandbox mechanics while Grant/OCE contracts retain authority.

### Candidate D — Hybrid

Use a narrow external runtime capability while retaining project-owned policy/data/evidence planes.

## 8.2 Explicitly not a candidate

A generalized “super-agent OS” in which the framework becomes:

- client relationship model;
- Grant domain model;
- canonical evidence model;
- policy constitution;
- autonomous submission authority;
- self-modifying product owner.

That architecture is outside scope.

## 8.3 Evaluation dimensions

Mandatory:

- constitutional fit;
- Dual-Hermes fit;
- tenant isolation;
- capability enforcement;
- worker/task isolation;
- session durability;
- restart/recovery;
- audit/replay compatibility;
- memory replaceability;
- secret boundary;
- MCP/tool-gateway integration;
- local-first development;
- cloud deployment path;
- observability;
- operational complexity;
- performance;
- dependency maturity;
- license;
- upstream churn risk;
- exit/rebuild cost;
- migration burden from G0 prototypes;
- amount of custom glue eliminated.

## 8.4 Hard gates

A runtime candidate is disqualified if it:

- weakens any Book 1 constitutional law;
- requires shared Personal/CEO memory;
- cannot enforce tenant separation;
- treats tool availability as authority;
- exposes durable credentials to agents;
- cannot preserve canonical Postgres/domain ownership;
- cannot integrate our evidence/audit IDs;
- cannot support task-scoped workers;
- makes framework state unreconstructable/export-hostile;
- cannot be exited without losing semantic business state.

## 8.5 Decision objective

Choose the substrate that removes the most generic runtime engineering **while changing the least product architecture**.

This is a cost/complexity optimization after architecture correctness—not a framework popularity contest.

---

# 9. Scanopy Decision — No Plan Amendment

Scanopy is a network/infrastructure discovery and documentation product. Its capabilities may become useful for later internal operations or hosted infrastructure observability, but they do not solve a current Grant-sector product requirement.

Disposition:

> **DEFER — do not add to G0 product dependencies, bake-offs, or runtime architecture.**

Reason:

- no direct Grant intelligence/application value;
- overlaps infrastructure-operations concerns rather than product runtime semantics;
- self-hosted licensing introduces AGPL considerations;
- current G0 already has sufficient observability/security/runtime planning without network-topology tooling.

This decision is intentionally recorded so the project does not revisit Scanopy simply because it is technically sophisticated.

---

# 10. Anti-Pollution Acceptance Tests

The amendment itself is only considered correctly applied if later planning/build agents can answer YES to all:

```text
Does Personal Hermes remain Personal Hermes?                 YES
Does CEO Hermes remain CEO Hermes?                           YES
Do our Intent/Task/Result contracts remain sovereign?        YES
Does Postgres/domain state remain canonical?                 YES
Does evidence authority remain Book 3/5 governed?            YES
Does Book 1 still authorize every real action?               YES
Are workers still bounded?                                   YES
Is submission still disabled?                                YES
Are external frameworks replaceable?                         YES
Are added candidates tied to an identified engineering gap?  YES
Did we avoid adding unrelated “cool” capabilities?           YES
```

Any NO means the implementation has violated this amendment.

---

# 11. Practical Impact on Current Execution

Books 0–1 currently being built should **not be interrupted or redesigned** because of these repository discoveries.

The changes introduced here are implementation-candidate amendments for later books.

The current execution flywheel remains:

```text
BUILD AGENT
Books 0–1
        ↓
external review / repairs / ratification
        ↓
Books 2–3
        ↓
Books 4–6 with bounded bake-offs from this amendment
        ↓
Book 7 evaluation/promotion architecture
        ↓
Book 8 vertical slice
        ↓
Book 9 runtime substrate ADR + clean repository
```

---

# 12. Final Amendment Rule

From this point forward, generic agent/runtime repositories do not enter G0 merely because they are powerful.

A new external project should amend the plan only if it does at least one of the following materially better than current candidates:

- grant-domain source connectivity;
- document/form extraction fidelity;
- deterministic eligibility/policy capability;
- secure tool/credential execution;
- tenant isolation;
- durable execution/recovery;
- evidence/provenance;
- evaluation/promotion quality;
- artifact/budget production;
- operational simplicity sufficient to replace significant custom infrastructure.

Otherwise disposition = REFERENCE / DEFER / REJECT without reopening architecture.
