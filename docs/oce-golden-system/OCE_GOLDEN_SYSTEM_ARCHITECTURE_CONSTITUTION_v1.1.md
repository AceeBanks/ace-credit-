# OCE Golden System
## Architecture Philosophy, Goal, Blueprint, and Constitution

**Document ID:** OCE-CONSTITUTION-001  
**Version:** 1.1  
**Status:** Ratified amended constitutional baseline  
**Owner and final authority:** Operator  
**Effective date:** 2026-08-17  
**Applies to:** OCE, PO, shared infrastructure, agents, applications, Quant Lab, Quant Watch, Cerebus integrations, execution systems, and every future system derived from this architecture

**Amendment A-001:** Adds the Holistic Build Cycle, governed learning from all build observations, bounded planning grammar, and the initial hybrid-cloud deployment profile.

---

## 0. Constitutional Status

This document is the permanent north star for the OCE ecosystem. It exists to prevent architectural drift, empty scaffolding, inflated capability claims, duplicated frameworks, unsafe automation, and short-term implementation choices that weaken the long-term system.

It is not a backlog, a sprint plan, or a description of whatever the repository happens to contain today. It defines what the system is intended to become, which properties may never be casually traded away, how present reality must be represented, and how future plans must be judged.

All future architecture documents, roadmaps, prompts, agents, applications, and code changes shall either conform to this constitution, identify the exact clause they extend, or submit a versioned constitutional amendment.

Silence is not approval. A feature that conflicts with this document does not become valid merely because it was implemented or passed isolated tests.

---

## 1. Preamble: The Golden System

The objective is not merely to build one strong application. The objective is to build the **golden system that reliably creates, tests, governs, operates, and improves good systems**.

OCE is that golden system.

PO is its principal reasoning, engineering, and orchestration intelligence.

Quant Lab, Quant Watch, Cerebus-powered research, trading automation, and future applications are products created on top of that foundation. They are important, but they are not allowed to redefine or bypass the foundation for local convenience.

The castle metaphor is literal architecture doctrine:

- the cloud is the ground and utilities;
- OCE is the foundation, structure, laws, corridors, security, records, and load-bearing frame;
- PO is the master builder operating within those laws;
- applications are the towers, rooms, instruments, and workshops;
- quant is one powerful wing of the castle, not the soil beneath it.

The quality ceiling of every future application is set by the quality of OCE. Therefore, system logic, contracts, authority, evidence, observability, and recoverability receive priority over feature count and visual polish.

---

## 2. Mission and North Star

### 2.1 Mission

Create a private, durable, high-dimensional operating environment in which an operator and governed agents can turn ideas into trustworthy systems through a repeatable chain of specification, construction, verification, deployment, observation, and controlled improvement.

### 2.2 North-star outcome

The ecosystem succeeds when the operator can express a goal and OCE can help PO:

1. understand the goal and its constraints;
2. inspect existing knowledge and capability honestly;
3. design a coherent system without duplicating the architecture;
4. build through bounded, observable actions;
5. verify real behavior rather than infer it from scaffolds;
6. preserve provenance, decisions, and evidence;
7. deploy safely to a private operating environment;
8. monitor, recover, and improve the result;
9. reuse the same machinery for a different domain;
10. never silently acquire authority over capital, production, credentials, or irreversible actions.

### 2.3 Governing equation

> **Useful autonomy = capability × evidence × control × recoverability**

If any factor approaches zero, claimed autonomy approaches zero. More tools without evidence and control do not create a more capable system; they create a larger hazard surface.

---

## 3. System Ontology

### 3.1 The Golden System

The Golden System is the reusable, domain-neutral machinery that makes other systems dependable. It includes identity and authority; canonical contracts and schemas; event and state management; planning and orchestration; tools and execution controls; memory and knowledge; evidence and evaluation; artifact and deployment lineage; observability, recovery, and incident handling; and constitutional governance.

OCE owns this layer.

### 3.2 The Builder

PO is the principal system-building intelligence operating through OCE. PO may research, reason, design, write, test, analyze, and propose actions. Its authority is always explicit, scoped, expiring where appropriate, and recorded.

PO is not a parallel framework and may not create an ungoverned substitute for OCE merely because doing so is faster.

### 3.3 Good Systems

Good Systems are domain applications built using Golden System services. Examples include Quant Lab, Quant Watch, Cerebus research and validation services, data tools, research agents, portfolio and risk tools, operational dashboards, and future business or engineering applications.

A Good System owns its domain logic. It does not duplicate constitutional infrastructure.

### 3.4 Domain kernels

A domain kernel contains logic that must be correct independent of agent reasoning. In quant, this includes calculations, market calendars, cost models, fill models, risk limits, order state, reconciliation, and portfolio accounting.

Domain kernels must be deterministic, testable, versioned, and callable by agents. An LLM may propose inputs or interpret results; it may not replace the kernel.

---

## 4. Foundational Philosophy

### Principle 1 — Systems over personalities

The system must not depend on a specific chat session, model personality, developer memory, or undocumented intuition. Durable contracts and evidence outrank recollection.

### Principle 2 — Truth before velocity

A smaller verified capability is more valuable than a broad unverified claim. Status language must describe demonstrated behavior.

### Principle 3 — Logic before code

Code is an implementation of system logic, not a substitute for it. Authority boundaries, states, failure behavior, invariants, and evidence requirements must be understandable before implementation is accepted.

### Principle 4 — Foundations before floors

Infrastructure precedes OCE hardening; OCE hardening precedes application layering; application architecture precedes domain expansion; controlled research precedes capital execution.

### Principle 5 — One spine, many domains

The ecosystem has one constitutional and event-governance spine. New applications extend it through contracts and adapters instead of creating independent agent frameworks.

### Principle 6 — Evidence outranks narrative

Documentation, test names, generated reports, and agent statements are claims. Reproducible observations are evidence. The system shall distinguish the two.

### Principle 7 — Deny by default

Unknown identity, missing permission, invalid state, absent evidence, stale data, or ambiguous intent results in refusal, quarantine, or escalation—not optimistic continuation.

### Principle 8 — Authority follows competence and risk

The ability to research does not imply permission to deploy. The ability to deploy does not imply permission to trade. The ability to propose an order does not imply permission to route capital.

### Principle 9 — Reversible first

Prefer preview, dry run, sandbox, paper, shadow, staged release, backups, and rollback. Irreversible actions require stronger proof and explicit approval.

### Principle 10 — High dimensional, cognitively legible

The architecture may be sophisticated, but its truth must remain explainable to the operator without requiring blind trust in code. Complexity belongs behind clear contracts, status views, and evidence.

### Principle 11 — Private by default

The system is designed for one operator. It should optimize for capability, security, and operational clarity rather than premature multi-tenant scale.

### Principle 12 — Provider independence

Cloud vendors, model providers, brokers, databases, and interfaces are replaceable dependencies. Constitutional contracts and durable data remain under operator control.

### Principle 13 — No observation is trash

Every meaningful attempt, error, contradiction, workaround, rejected approach, unexpected success, and operator correction is potential system knowledge. It must receive an explicit disposition: retain, normalize, summarize, redact, quarantine, expire, or delete with a recorded reason.

This principle does not require infinite raw-log retention. It prohibits silent loss of learning value.

### Principle 14 — Building is itself a research domain

OCE and PO do not only build applications. They study how systems are built: which instructions produce clarity, which tools fail, which environment assumptions recur, which tests provide false confidence, and which practices repeatedly improve outcomes.

Validated build knowledge becomes playbooks, tests, templates, policies, tools, or architectural improvements.

### Principle 15 — Plan deeply, commit narrowly

The full architecture remains visible, but implementation advances through bounded blocks. Each block is articulated, challenged, revised, approved, built, verified, and learned from before downstream dependency is treated as stable.

---

## 5. Goals and Non-Goals

### 5.1 Primary goals

- Build an honest inventory of what OCE and PO can currently do.
- Convert partial capability into verified end-to-end capability.
- Create a reusable pipeline for producing governed applications.
- Preserve decisions, evidence, lineage, and state across sessions and machines.
- Operate primarily from a cost-efficient private cloud control plane.
- Allow powerful workloads through operator-owned or temporary workers.
- Support agents that can research and build without gaining accidental authority.
- Make every consequential action observable, attributable, and recoverable.
- Enable quant research and eventual execution through the same constitutional machinery.

### 5.2 Explicit non-goals

- A second competing agent framework.
- A collection of impressive but disconnected scaffolds.
- Autonomous live trading as an early milestone.
- An unrestricted shell-wielding agent exposed to the public internet.
- Kubernetes or hyperscale complexity before the workload demands it.
- Multi-tenant SaaS architecture for a one-user system.
- Treating an LLM as a database, risk engine, simulator, ledger, or source of deterministic truth.
- Declaring systems complete because unit tests pass.
- Maximizing lines of code, agent count, or feature count.
- Preserving legacy code merely because it exists.

---

## 6. Constitutional Architecture

~~~mermaid
flowchart TD
    OP["Operator: intent and final authority"]
    APP["Applications: Quant Lab, Quant Watch, future tools"]
    PO["PO: reasoning, engineering, orchestration"]
    OCE["OCE: governance, contracts, events, evidence"]
    INFRA["Private cloud and governed workers"]

    OP --> APP
    OP --> PO
    APP --> OCE
    PO --> OCE
    OCE --> INFRA
~~~

The diagram expresses authority and dependency, not merely network traffic:

- the operator owns intent and final authority;
- applications provide domain interfaces and request services;
- PO reasons and builds;
- OCE mediates identity, state, permissions, execution, and evidence;
- infrastructure supplies durable compute, storage, networking, and recovery.

No upper layer may reach through a lower layer to bypass its controls.

---

## 7. Architectural Planes

### 7.1 Infrastructure Plane

Provides private networking, compute, durable storage, backups, secrets, process supervision, and worker connectivity.

Initial doctrine:

- one cost-efficient Linux control-plane server;
- private access through an authenticated overlay network;
- containers or supervised services, without premature orchestration complexity;
- PostgreSQL as durable operational truth;
- Redis only for transient queues, coordination, locks, and caches;
- Parquet plus DuckDB for local analytical data where appropriate;
- object storage for immutable artifacts and backups;
- isolated Windows/MT5 worker when required;
- temporary CPU/GPU workers for burst workloads;
- encrypted off-site backups with restore tests.

The first cloud implementation is intentionally light. “Light” means operationally simple, not architecturally careless.

### 7.2 Identity and Authority Plane

Every human, agent, service, application, tool, credential, and worker has an identity. Every consequential action is evaluated against a capability grant defining actor, action, target scope, environment, limits, approval requirements, expiration, and audit identity.

Role names alone are insufficient. Permissions are explicit capabilities.

### 7.3 Event and State Plane

OCE maintains canonical event envelopes, legal state transitions, idempotency, causality, retries, and failure semantics.

Every durable event must identify its event ID and type, schema version, actor and authority, timestamp and causal parent, target object, input and artifact hashes, environment, result or failure, and evidence references.

State transitions that cannot be explained and replayed are invalid.

### 7.4 Memory and Knowledge Plane

Memory is divided by function:

- **constitutional memory:** governing rules and amendments;
- **architectural memory:** contracts, decisions, diagrams, and invariants;
- **operational memory:** current state, incidents, deployments, and tasks;
- **research memory:** sources, hypotheses, experiments, and results;
- **episodic memory:** agent sessions and action traces;
- **artifact memory:** code, models, datasets, reports, and manifests.

Retrieval systems may help locate memory. They do not replace authoritative records. Facts must retain source, time, confidence, and status.

### 7.5 Reasoning and Planning Plane

PO and subordinate agents translate intent into bounded plans. Planning output must separate known facts, assumptions, unknowns, constraints, proposed actions, required permissions, verification criteria, and rollback.

Reasoning may be probabilistic. State transitions and permissions are not.

### 7.6 Tool and Execution Plane

Tools are governed actuators. Shell, Python, file mutation, Git, browser actions, APIs, process control, deployments, and broker commands are capabilities—not generic conveniences.

Each invocation is classified as read-only, reversible mutation, consequential mutation, privileged or externally irreversible, or capital-bearing. Higher classes require progressively stronger isolation, approval, verification, and audit.

### 7.7 Evidence and Validation Plane

Evidence is a first-class product of work. It includes test results, environment manifests, input/output hashes, logs and traces, benchmark results, end-to-end runs, restart and recovery tests, security findings, and unresolved contradictions.

Tests are evidence only for the behavior they actually exercise.

### 7.8 Product and Application Plane

Applications are thin domain shells over shared Golden System services. They may own domain workflows, UI, models, data, and deterministic kernels. They may not silently duplicate identity, permissions, lifecycle governance, event lineage, memory policy, deployment evidence, or incident handling.

### 7.9 Quant Domain Plane

Quant is downstream of the platform and inherits its controls.

Shared quant foundations include canonical instruments and symbology; UTC, DST, exchange calendar, and session normalization; dataset manifests and quality rules; reproducible statistics; executable cost, slippage, and fill models; backtest provenance; portfolio and risk accounting; and execution journal, reconciliation, and restart behavior.

Strategy-specific logic includes market hypothesis and mechanism; features and states; entry, exit, and invalidation; parameter domain; capacity and decay; activation policy; and instrument-specific execution lifecycle.

### 7.10 Build Intelligence Plane

The Build Intelligence Plane converts construction activity into reusable institutional knowledge. It captures:

- plans, assumptions, decisions, and rejected alternatives;
- prompts, tool calls, environment state, and artifact lineage;
- failures, partial successes, retries, workarounds, and fixes;
- operator corrections and judgments;
- recurring error signatures and their valid scopes;
- validated build practices and counterexamples.

Raw observations never become doctrine automatically. They pass through:

> observe → normalize → classify → associate → hypothesize → validate → promote or reject

Promoted knowledge must state evidence, scope, confidence, recurrence, exceptions, and expiration or review conditions. A one-time coincidence is not a universal practice.

---

## 8. Constitutional Articles

### Article I — Operator sovereignty

The operator is the final authority over constitutional changes, production deployment, credentials, external publication, financial commitments, and capital-bearing actions. Agents may advise, challenge, and present evidence. They may not reinterpret silence as consent.

### Article II — Honest truth labels

Every component and capability must carry an evidence-bounded status:

1. **IDEA** — concept only;
2. **SPECIFIED** — behavior and acceptance criteria defined;
3. **SCAFFOLDED** — interfaces or structure exist without proven behavior;
4. **IMPLEMENTED_UNVERIFIED** — meaningful code exists but behavior is not established;
5. **VERIFIED_ISOLATED** — verified within a bounded component;
6. **VERIFIED_INTEGRATED** — verified across defined integrations;
7. **VERIFIED_E2E** — demonstrated through the complete intended path;
8. **OPERATIONALLY_PROVEN** — repeated successfully under realistic operation, restart, and failure;
9. **QUARANTINED** — present but prohibited from ordinary use;
10. **FALSIFIED** — claimed behavior disproven;
11. **DEPRECATED** — retained temporarily but no longer authoritative.

“Implemented” never means “works end to end.” Promotion requires linked evidence. Demotion is permitted whenever contradictory evidence appears.

### Article III — Deny by default

Missing permission, missing evidence, stale state, unresolved identity, invalid schema, unknown environment, or ambiguous target causes a stop, quarantine, or request for operator direction.

### Article IV — Separation of duties

Research, proposal, approval, execution, verification, and reconciliation are distinct functions. They may use related services but must remain separately visible and independently testable. No agent should both invent the success criterion and unilaterally certify that it passed.

### Article V — Deterministic kernels

Calculations, accounting, schemas, permissions, state machines, risk checks, order handling, and reconciliation live in deterministic code with tests. LLMs may generate hypotheses, specifications, explanations, and candidate code. They may not become the source of numerical or transactional truth.

### Article VI — Canonical contracts

Shared concepts are defined once, versioned, and reused. Adapters may translate external formats into canonical contracts; applications may not fork their meaning without an approved architectural decision.

### Article VII — Provenance and replay

Every important result identifies exact inputs, code or artifact version, configuration, environment, actor, timestamps, and transformations. If exact reproduction is impossible, the system records why and defines the closest valid replay.

### Article VIII — Fail closed

Safety-critical and capital-bearing paths fail closed. Timeouts, service loss, partial writes, uncertain acknowledgements, stale market state, and reconciliation gaps may not be interpreted as success.

### Article IX — Memory with lineage

Memory must never collapse proposal, belief, evidence, and decision into one undifferentiated record. All durable claims retain provenance and status.

### Article X — Bounded tool authority

Tool authority is least-privilege, task-scoped, environment-aware, observable, and revocable. Dangerous capabilities require explicit gates and must not be granted merely to reduce friction.

### Article XI — Governed self-improvement

OCE and PO may identify weaknesses, propose changes, construct candidates, and run evaluations. They may not silently rewrite constitutional controls, elevate their own permissions, modify evaluation criteria after seeing results, or deploy their own replacements without approval.

Self-improvement means governed iteration, not self-authorized mutation.

### Article XII — Source and branch authority

The registry and an explicit branch map define what is canonical. Branch names such as “main,” “master,” “test,” or “research” do not establish truth by themselves.

For the existing system, current precedence is:

1. operator clarification;
2. hash-frozen approved contract;
3. supplied implementation source where explicitly designated;
4. authoritative manuals and domain doctrine;
5. Capital Routing conventions;
6. MVE doctrine;
7. legacy branches as untrusted reference.

Conflicts must be recorded, not silently blended.

### Article XIII — Private security boundary

The control plane remains private by default. Public access, if later required, terminates at a narrow authenticated interface. Internal administration, shells, databases, queues, broker adapters, and agent execution are not exposed directly.

Secrets never belong in source control, prompts, logs, generated reports, or artifacts. Suspected exposed secrets are rotated, not merely deleted.

### Article XIV — Resource and entropy discipline

The architecture distinguishes source, dependencies, caches, datasets, artifacts, logs, and backups. A large workspace is not automatically a large application.

Clean deployments are built from declared source and manifests. Local clutter, virtual environments, caches, historical datasets, and Git objects are not copied blindly into production.

### Article XV — Observability and recovery

Every durable service exposes health, readiness, structured logs, metrics, correlation IDs, and failure state. Every important workflow defines retry, idempotency, timeout, quarantine, and operator recovery. Backups without a tested restore are unverified.

### Article XVI — Constitutional change

No implementation may weaken these articles through convenience defaults. An amendment requires proposed language, motivation, affected invariants, risk analysis, migration, tests and evidence, rollback, operator ratification, and a new versioned decision record.

### Article XVII — Holistic build-cycle conservation

Every governed build produces two outputs:

1. the intended system artifact; and
2. knowledge about the process that produced it.

OCE must preserve enough context to explain what was attempted, why it was attempted, what actually happened, how the result was verified, what failed, what changed, and what should be reused or avoided.

Errors are first-class observations, not embarrassing debris. Failed attempts must remain distinguishable from successful implementations and may never be rewritten into a clean fictional history.

Retention remains governed. Secrets, personal data, licensed material, redundant noise, and hazardous payloads may be redacted or deleted. Their disposition, category, and reason remain recorded without preserving the unsafe content.

### Article XVIII — Bounded planning grammar

All program planning uses the hierarchy:

> **Block → Chapter → Section**

The canonical identifier is `B{block}.C{chapter}.S{section}`.

- A block contains no more than five chapters.
- A chapter contains no more than five sections.
- A section is the smallest constitutional planning unit and must be independently understandable, reviewable, and gateable.
- Tasks may exist beneath a section, but tasks do not create hidden architecture or silently expand scope.
- If more than five chapters or sections are required, the work must be decomposed into another block or chapter.

Each section must define purpose, current truth, target state, governing questions, invariants, dependencies, decisions, failure modes, evidence, exit gate, learning hooks, and unresolved matters.

No section advances to build solely because it has been written. It advances after operator review and explicit readiness.

### Article XIX — Stable core and disposable power

The infrastructure separates durable authority from elastic computation:

- OCE state, registry, identity, PostgreSQL, secrets, and canonical artifacts live on a stable private control plane.
- Marketplace, decentralized, GPU, and burst workers are disposable executors.
- Disposable workers receive minimum scoped data and credentials, produce hashed artifacts, return evidence, and terminate.
- No burst worker becomes the sole holder of authoritative memory, irreplaceable data, broker credentials, or capital authority.
- Provider choice remains replaceable; role separation is constitutional.

---

## 9. Authority Model

| Actor | May do | May not do without explicit approval |
|---|---|---|
| Operator | Set goals, approve architecture, grant authority, deploy, authorize capital | None within lawful ownership; the system should still warn and preserve evidence |
| OCE governance | Enforce contracts, states, permissions, evidence gates, and audit | Invent strategic goals, conceal failures, waive constitutional rules |
| PO | Research, reason, design, code, test, propose, and orchestrate within grants | Self-grant authority, expose services, use capital, deploy consequential changes |
| Worker agent | Execute a bounded task with specified tools and acceptance criteria | Expand scope, delegate authority it lacks, declare global completion |
| Application | Submit intents, display state, execute approved domain workflows | Bypass OCE controls or redefine shared truth |
| Deterministic risk service | Admit, reject, or size requests under versioned rules | Invent alpha, relax limits, approve its own rule changes |
| Execution service | Route authorized intents and report actual outcomes | Create intent, infer approval, treat uncertain state as complete |
| Evaluator | Test against frozen criteria and report evidence | Modify the candidate or post-hoc redefine success |

---

## 10. Canonical Contracts

The minimum shared language consists of:

- **ActorIdentity** — who or what is acting;
- **CapabilityGrant** — exactly what authority exists;
- **TaskIntent** — requested outcome, scope, constraints, and owner;
- **WorkflowPlan** — proposed actions, dependencies, gates, and rollback;
- **EventEnvelope** — canonical causal and audit wrapper;
- **ArtifactManifest** — content hash, provenance, dependencies, and status;
- **DatasetManifest** — source, period, schema, quality, lineage, and allowed use;
- **EvaluationProtocol** — frozen success criteria and test design;
- **EvaluationReport** — results, environment, evidence, limitations, and verdict;
- **DeploymentManifest** — release, configuration, target, approvals, and rollback;
- **IncidentRecord** — failure, impact, containment, cause, and correction;
- **ConstitutionalDecision** — approved architectural interpretation or amendment;
- **StrategySpec** — hypothesis, market scope, logic, risks, and invalidation;
- **BacktestRun** — engine, code, data, costs, parameters, and result lineage;
- **OrderIntent** — proposed financial action before risk admission;
- **RiskDecision** — deterministic approval, rejection, sizing, and rule version;
- **ExecutionReport** — actual broker or venue acknowledgements and fills;
- **ReconciliationReport** — comparison among intent, internal state, and external truth;
- **DriftReport** — deviation among specification, implementation, operation, and documentation.
- **BuildObservation** — attributable raw fact from a build or operational attempt;
- **FailureObservation** — failed or degraded behavior with context, evidence, and impact;
- **AttemptRecord** — intent, plan, environment, actions, outputs, retries, and disposition;
- **LessonCandidate** — proposed learning that has not yet earned authority;
- **PracticePattern** — validated reusable method with scope, confidence, and exceptions;
- **RetentionDecision** — governed keep, summarize, redact, quarantine, expire, or delete decision.

Contracts must be machine-validatable and human-readable.

---

## 11. Mandatory Lifecycles

### 11.1 General system lifecycle

~~~mermaid
flowchart TD
    I["Intent"] --> S["Specification"]
    S --> B["Bounded build"]
    B --> V["Verification"]
    V --> E["End-to-end proof"]
    E --> R["Release decision"]
    R --> O["Observed operation"]
    O --> L["Learning and governed change"]
~~~

Each transition requires evidence appropriate to its risk. Failure returns the object to the correct earlier state; it does not get relabeled as success.

### 11.2 Governed agent action lifecycle

1. Receive an attributable intent.
2. Resolve identity, target, environment, and scope.
3. Separate facts, assumptions, and unknowns.
4. Produce or retrieve the applicable specification.
5. Classify action risk.
6. Check capabilities and required approval.
7. Prefer a dry run or isolated execution.
8. Execute with correlation and idempotency controls.
9. Verify the real side effect independently.
10. Record result, evidence, failure, and residual uncertainty.
11. Update status only to the level supported by evidence.

### 11.3 Quant research-to-capital lifecycle

The canonical sequence is:

> idea → strategy specification → fast falsification filter → genuine engine backtest → holdout → walk-forward → cost/slippage stress → paper → shadow → proposal → live only with explicit approval

Promotion requires frozen inputs, a registered strategy identity, reproducible results, cost realism, and independent risk evaluation. Research completion never implies execution authority.

---

## 12. Cloud and Deployment Doctrine

The immediate cloud goal is a simple, economical, powerful private base—not a finished distributed platform.

### 12.1 Initial topology

- Linux control plane for OCE API, PO services, scheduler, registry, PostgreSQL, Redis, observability, and private UI;
- private network overlay for operator and worker access;
- object backup separate from the server;
- operator computer as an optional governed worker, not the sole durable state;
- isolated Windows worker for MT5 or Windows-only execution;
- temporary burst nodes for heavy research, compilation, or GPU work.

### 12.2 Deployment rules

- Deploy clean, versioned releases from declared source.
- Do not upload the entire local workspace.
- Infrastructure is reproducible from configuration and manifests.
- Databases have migrations, backups, retention, and restore drills.
- Every service has a health check and restart policy.
- Development, test, paper/shadow, and live environments are distinguishable.
- No capital-bearing credential exists in a development environment.
- A provider must be replaceable without redesigning OCE contracts.

### 12.3 Intentionally deferred

Kubernetes, automatic horizontal scaling, multi-region active-active systems, multi-user tenancy, permanent GPU ownership, and public product exposure are deferred until proven workload or reliability needs justify them.

### 12.4 Initial reference deployment profile

The first implementation profile, dated 2026-08-17, is:

- **Stable control plane:** Netcup RS 4000 G12 — 12 dedicated AMD EPYC cores, 32 GB ECC RAM, 1 TB NVMe, listed at €39.92/month including German VAT.
- **Growth option:** Netcup RS 8000 G12 — 16 dedicated cores, 64 GB ECC RAM, 2 TB NVMe, listed at €71.36/month including German VAT.
- **Private network:** Tailscale, beginning with the eligible single-operator tier.
- **Off-server backup:** Backblaze B2 or a contract-compatible S3 interface with equivalent restore behavior.
- **Burst compute:** OctaSpace as the first experimental marketplace, with RunPod as the conventional fallback.

The expected active-development budget for the RS 4000 profile is approximately $65–$80 per month when using roughly 50 hours of marketplace GPU capacity. Provider prices are operating assumptions, not constitutional invariants.

OctaSpace is approved only for disposable workloads until its reliability, data handling, performance, billing, and artifact-return behavior are experimentally verified. Initial funding should be deliberately small because deposited service credits are non-refundable and storage, traffic, and conversion costs may apply.

---

## 13. OCE and PO Tightening Doctrine

OCE tightening is not a cosmetic refactor. It is a reality-sealing program.

### 13.1 First obligation: establish reality

Before expanding features, the system must produce:

- complete repository and branch map;
- inventory of services, modules, contracts, tools, tests, and entry points;
- dependency and import graph;
- capability matrix with truth labels;
- executable installation path;
- end-to-end scenarios;
- security and credential inventory;
- data and storage inventory;
- contradiction and duplicate-framework register.

### 13.2 Empty-scaffold rule

A class, handler, endpoint, agent, or engine that returns success-shaped output without performing and verifying the claimed work is a scaffold. It must be labeled **SCAFFOLDED** or **IMPLEMENTED_UNVERIFIED**, never complete.

### 13.3 Consolidation rule

Duplicated orchestration, memory, event, identity, or tool systems must be designated canonical, adapted behind the canonical contract, quarantined, migrated, or removed after evidence-preserving deprecation.

### 13.4 PO quality bar

PO is operationally mature only when it can repeatedly recover context from authoritative memory; plan against explicit contracts; use tools within capabilities; survive partial failure and restart; verify side effects; produce auditable artifacts; distinguish uncertainty from completion; hand work to another session without hidden state; and build a small application end to end through OCE.

---

## 14. Application Doctrine

An application is accepted as an OCE-native Good System when:

1. it registers identities, contracts, artifacts, and lifecycle;
2. it uses shared authority and event mechanisms;
3. it has a deterministic domain kernel where correctness matters;
4. it emits evidence for meaningful outcomes;
5. it can be installed, tested, deployed, observed, and recovered;
6. it cannot bypass production or capital gates;
7. its status makes capability understandable to the operator;
8. its documentation is generated from or checked against operational truth.

The first reference application should be narrow enough to finish but rich enough to exercise the entire Golden System. Its purpose is to prove the factory, not to become the final castle.

---

## 15. Anti-Drift Operating System

### 15.1 Canonical registry

A registry identifies the authoritative version and status of every contract, service, agent, tool, dataset, model, strategy, application, deployment, and constitutional document.

### 15.2 Architecture Decision Records

Meaningful design choices are written as versioned decisions containing context, alternatives, choice, consequences, and supersession.

### 15.3 Invariant tests

Constitutional properties become automated tests where possible:

- no tool executes without attributable identity;
- no status promotion lacks evidence;
- no live order bypasses risk admission;
- no event omits schema version and causal identity;
- no secret appears in source or logs;
- no application defines a parallel permission system;
- no deployment lacks rollback metadata.

### 15.4 Reality audits

At defined checkpoints, architecture claims are compared with repository state, runtime behavior, deployed services, and documentation. Contradictions create Drift Reports.

### 15.5 Frozen gates

Acceptance criteria are frozen before the evaluated run. Changing them creates a new evaluation version.

### 15.6 Branch and artifact map

Every active branch and release has an explicit purpose and authority. Experimental history is preserved without allowing it to masquerade as production truth.

### 15.7 Documentation rule

Documentation may lead implementation as specification or follow implementation as verified description, but its status must say which. Future tense and current capability may not be blended.

### 15.8 Build Learning Ledger

Every section maintains a Build Learning Ledger linking Attempt Records, Build Observations, Failure Observations, operator corrections, Lesson Candidates, and promoted Practice Patterns.

The ledger is append-preserving. Corrections supersede earlier interpretations without erasing the original event.

### 15.9 Planning integrity

Every plan identifies its constitutional version, block, chapter, section, dependencies, truth status, owner, and exit gate. Cross-block work may be explored, but it may not silently create a downstream dependency before the upstream gate is satisfied.

---

## 16. Constitutional Build Order

This sequence is binding at the program level. Detailed plans may change, but they may not invert the dependency logic without amendment.

### Stage 0 — Seal the north star

Ratify this constitution, establish its canonical location, create the master Block/Chapter/Section map, and require future work to reference its constitutional and planning versions.

### Stage 1 — Establish the light cloud foundation

Create the private control plane, durable database, basic queue, backups, secrets, observability, and governed worker connection. Prove deployment and restore at minimal complexity.

### Stage 2 — Establish OCE reality

Audit the full repository and lineage. Map what exists, what runs, what is scaffolded, what is duplicated, and what is dangerous. Produce the capability registry and select canonical sources.

### Stage 3 — Tighten the Golden System

Repair installation and imports; consolidate contracts; enforce identity, permissions, events, lifecycle, evidence, and recovery; close security gaps; prove complete OCE/PO workflows.

This stage receives the greatest architectural attention.

### Stage 4 — Prove the application factory

Build one narrow reference application entirely through the tightened OCE/PO path. Demonstrate intent-to-deployment, evidence, restart, observation, and governed improvement.

### Stage 5 — Build reusable application surfaces

Create stable APIs, SDKs, templates, UI primitives, domain adapters, and operator views so future tools inherit the system rather than rebuild it.

### Stage 6 — Integrate Quant Lab and Quant Watch

Bring quant data, research, Cerebus logic, testing, portfolio logic, and monitoring into the canonical contracts and lifecycle.

### Stage 7 — Controlled execution

Introduce paper, shadow, reconciliation, and finally explicitly approved live pathways only after underlying states and gates are operationally proven.

---

## 17. Stage Exit Gates

| Stage | Minimum proof required to advance |
|---|---|
| Cloud foundation | Clean deploy, private access, health visibility, backup, successful restore |
| OCE reality | Complete inventory, executable paths tested, capability labels evidenced, hazards identified |
| OCE tightening | End-to-end agent workflow, permission denial proof, restart/recovery proof, auditable artifacts |
| Application factory | One OCE-native app built, tested, deployed, observed, and changed without bypass |
| Application surfaces | A second app reuses contracts and services with materially less custom platform code |
| Quant integration | Reproducible datasets and backtests, genuine holdout/walk-forward/cost stress, lineage complete |
| Controlled execution | Paper and shadow reconciliation, failure drills, independent risk gates, operator approval |

Passing a later-looking demo does not waive an earlier gate.

---

## 18. Definition of Architectural Success

OCE is successful when it can repeatedly produce trustworthy systems, not when it merely contains many components.

The Golden System shall eventually demonstrate:

- a fresh machine can install it from declared source;
- current capability can be understood without reading the entire codebase;
- agents operate under explicit, inspectable grants;
- one intent can be traced through plan, actions, artifacts, tests, deployment, and operation;
- interrupted workflows recover without corrupting truth;
- results can be reproduced or their non-reproducibility explained;
- applications reuse shared foundations;
- models, providers, and cloud hosts can be exchanged through adapters;
- a new domain can be added without duplicating governance;
- no system can silently move from research to capital execution;
- the operator can see what is real, uncertain, failed, and awaiting decision.
- failed attempts remain explainable rather than disappearing from history;
- recurring build errors can be retrieved across projects and sessions;
- validated lessons can become tests, tools, templates, and policies;
- an artifact and the process knowledge that produced it remain causally linked.

---

## 19. The Constitutional Kernel

This compact kernel should be included in future agent and project instructions:

1. OCE is the one Golden System; do not create a competing framework.
2. Cloud first, OCE/PO second, applications third, quant downstream.
3. State current truth using evidence-bounded labels.
4. Treat scaffolds as scaffolds, tests as scoped evidence, and demos as demonstrations.
5. Use canonical contracts, identities, events, and lifecycles.
6. Deny by default; never infer consequential authority.
7. Keep deterministic truth outside the LLM.
8. Separate proposal, approval, execution, verification, and reconciliation.
9. Record provenance, causal lineage, environment, and artifact hashes.
10. Prefer reversible, private, observable, recoverable operations.
11. Promote capability only after frozen criteria and real end-to-end proof.
12. If a change conflicts with the constitution, stop and propose an amendment.
13. Treat every meaningful build outcome as a learning observation with an explicit disposition.
14. Plan through bounded Blocks, Chapters, and Sections; never exceed five at either planning layer.
15. Keep durable authority on the stable core and use marketplace compute only as disposable power.

---

## 20. Current Reality Baseline

At ratification, the repository history contains meaningful architecture and implementation, but branch names and test presence do not establish a complete operating system.

The working assumptions to verify during the reality audit are:

- the connected private repository is `dabiggestpoppa/larger-lab`, with `main` currently designated as the GitHub default branch;
- active architectural lineage is distributed across branches including `main`, `master`, `capital-routing`, `cerebus-mve-implementation`, `tb-forward-engine`, and agent/research branches;
- the fuller OCE lineage exists across legacy and development branches rather than solely in the current main line;
- substantial production and test code exists;
- PO has genuine reasoning and tool-use capability;
- some execution, spawning, browser, healing, and infrastructure surfaces are partial or success-shaped scaffolds;
- full clean-install and end-to-end operational capability has not yet been proven;
- powerful mutation tools and historical credential exposure create a serious security boundary;
- the local workspace size includes more than deployable source and should not be copied wholesale to cloud infrastructure.

These statements are a starting hypothesis for audit, not permanent truth. The capability registry will replace them with evidence.

---

## 21. Ratification and Amendment Record

### Founding ratification

This document becomes authoritative when the operator confirms it as the baseline. Ratification does not claim the current code satisfies the constitution. It commits future work to measure and close the gap honestly.

### Amendment A-001 — Holistic Build Cycle and Hybrid Cloud

- **Date:** 2026-08-17
- **Proposer:** Operator and architecture assistant
- **Clauses added:** Principles 13–15, Build Intelligence Plane, Articles XVII–XIX, build-learning contracts, reference cloud profile, Build Learning Ledger, bounded planning grammar
- **Purpose:** Make construction itself a governed learning system, prevent loss of error-derived knowledge, control planning complexity, and formalize stable-core/disposable-compute separation
- **Compatibility:** Additive; it strengthens rather than weakens the founding articles
- **Rollback:** Restore Constitution 1.0 while retaining A-001 as a rejected amendment record
- **Decision:** Ratified by operator instruction to publish the baseline to the repository's main branch on 2026-08-17

### Amendment template

- Amendment ID:
- Proposer:
- Date:
- Clauses affected:
- Current constraint:
- Proposed language:
- Alternatives considered:
- Risk introduced:
- Evidence required:
- Migration:
- Rollback:
- Operator decision:

---

## Closing Declaration

We are not building automation that merely moves faster. We are building an environment that can think broadly, act powerfully, remain honest about what it knows, and preserve human sovereignty over what matters.

The ambition is maximal; the foundations are disciplined.

OCE is the Golden System. PO is the governed builder. Applications are its creations. Quant is a domain of application. Evidence is the currency of truth. Authority is explicit. Risk precedes return. The castle rises only as high as the foundation can actually carry.
