# G0 Book 1 — Product Constitution & Authority

**Document ID:** GS-G0-B1-CONST-001  
**Version:** 0.1  
**Status:** PROVISIONAL — SUBJECT TO BOOK 0 RATIFICATION AND BOOK 1 TESTS  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-24

---

# Preamble

This system exists to help organizations discover, understand, prepare for, and pursue grant opportunities through a governed Grant Intelligence and Application Production platform.

The platform may use multiple AI agents, deterministic services, data sources, external tools, and human reviewers. None of those components individually constitute the product's authority.

The system shall preserve a strict distinction between:

1. **relationship intelligence** — understanding the client and translating intent;
2. **operational intelligence** — planning and executing authorized work;
3. **canonical truth** — durable system state and evidence;
4. **bounded work** — disposable specialist execution;
5. **human authority** — approval over consequential actions.

Hermes is an operator of the platform, not the platform itself.

---

# Article I — Canonical Truth

## Law 1.1 — Agent memory is not system truth

No Personal Hermes memory, CEO Hermes memory, specialist-agent memory, prompt context, sidechain summary, or conversational transcript is authoritative operational truth merely because an agent retains it.

Canonical operational state must live in governed durable storage and typed domain records.

## Law 1.2 — Durable truth survives agent replacement

The system must remain operable if any Hermes instance, model provider, specialist worker, prompt, or skill is reset, replaced, upgraded, or removed.

## Law 1.3 — External truth requires provenance

External facts become promotable only when tied to a registered source, immutable source snapshot, extraction/normalization event, freshness state, and contradiction status.

---

# Article II — Bounded Authority

## Law 2.1 — Tool possession is not permission

An agent does not gain authority merely because a tool exists or is technically callable.

## Law 2.2 — Capability grants are explicit

Every consequential operation must be represented by a typed capability with actor class, authority level, tenant/resource scope, approval rules, audit obligations, and failure semantics.

## Law 2.3 — Unknown authority fails closed

Unknown actor, capability, tenant, resource scope, or policy state must produce DENY or explicit human escalation rather than inferred permission.

---

# Article III — Human Sovereignty

## Law 3.1 — Human consequential-action control

Externally consequential actions remain human-governed until explicitly ratified otherwise.

## Law 3.2 — Submission is high consequence

Grant submission, signing, certification, legally material attestation, external commitment, and equivalent irreversible actions require L5 authority and explicit policy approval.

## Law 3.3 — Automation may prepare but not silently bind

Agents may research, draft, validate, prepare forms, and stage submission packages within granted scope; preparation does not imply permission to submit.

---

# Article IV — Dual-Hermes Separation

## Law 4.1 — Personal Hermes role

Personal Hermes exists to understand the client, preserve relationship continuity, clarify goals, maintain curated client context, and translate conversational intent into typed operational packets.

## Law 4.2 — CEO Hermes role

CEO Hermes exists to translate authorized intent into plans, delegate bounded work, supervise system workflows, synthesize results, propose repairs/improvements, and operate the application within policy.

## Law 4.3 — Context separation

Personal Hermes and CEO Hermes must not share one unbounded mutable memory namespace.

## Law 4.4 — Feed-forward boundary

Raw client history does not automatically propagate to CEO/workers. Raw worker execution does not automatically propagate to Personal Hermes.

Typed intent, task, result, outcome, and explanation packets are the preferred communication boundary.

---

# Article V — Worker Doctrine

## Law 5.1 — Workers are bounded and disposable

Specialist agents receive only the information and capability required for an assigned task.

## Law 5.2 — Workers do not inherit parent authority

Delegation does not transfer all CEO authority to a worker.

## Law 5.3 — Worker traces are sidechains

Full execution traces belong in governed sidechain/audit storage. Parent active context receives only bounded result packets and references.

---

# Article VI — Deterministic Supremacy

## Law 6.1 — Deterministic questions use deterministic services

Once source language has been normalized into explicit rules, deterministic services decide:

- grant eligibility predicates;
- numerical arithmetic;
- deadlines/date comparisons;
- identifier validity;
- requirement completion state;
- budget reconciliation;
- schema validity;
- capability authorization.

## Law 6.2 — LLM interpretation is not final authority

Models may assist in converting ambiguous language to candidate structured rules, but those rules require validation and their subsequent evaluation is deterministic.

---

# Article VII — Evidence Before Promotion

## Law 7.1 — Claims require lineage

A claim intended for grant research, matching, eligibility, proposal text, or client advice must be traceable to evidence or explicitly labeled unverified/inferred.

## Law 7.2 — Source authority is explicit

Official/current issuer records generally outrank stale, secondary, or user-provided representations for facts under the issuer's authority, subject to fact-specific precedence policy.

## Law 7.3 — Conflicts are not silently erased

Conflicting facts must be resolved through precedence, refresh, merge rules, or human escalation. Silent overwrite is prohibited.

---

# Article VIII — Memory & Learning

## Law 8.1 — Selective continuity over infinite memory

The system optimizes for useful continuity, reconstructability, and promoted lessons rather than permanent active retention of all history.

## Law 8.2 — Learning requires promotion

Observations are not durable doctrine until validated and promoted through the defined learning lifecycle.

## Law 8.3 — Superseded information must not remain co-equal

When a fact or lesson is superseded, active memory and canonical state must reflect that status rather than silently preserving contradictory versions as equally current.

---

# Article IX — Secrets & Sensitive Data

## Law 9.1 — Secrets never belong in conversational memory

Passwords, API keys, reusable tokens, private credentials, and equivalent secrets may not be stored in Personal Hermes memory, CEO Hermes memory, worker sidechains, prompts, ordinary logs, or Git.

## Law 9.2 — Agents receive capabilities, not durable credentials

External credentials must be scoped and injected server-side through approved gateways or service identities.

## Law 9.3 — Least data necessary

Agents and services receive only the tenant/project data necessary for their assigned operation.

---

# Article X — Multi-Tenant Isolation

## Law 10.1 — Tenant scope is mandatory

Every governed resource and consequential action must resolve to an authorized tenant/project scope where applicable.

## Law 10.2 — Cross-tenant leakage is a constitutional failure

Any path permitting one tenant's data, artifacts, memory, credentials, or workflows to be exposed to another tenant is P0 severity.

---

# Article XI — Auditability

## Law 11.1 — Consequential actions are attributable

Every consequential operation must record, where applicable:

- actor identity;
- tenant/project;
- capability;
- target resource;
- request ID;
- timestamp;
- policy/approval decision;
- result;
- evidence/artifact references;
- error/rollback state.

## Law 11.2 — Audit history is not agent memory

Audit records are durable system evidence and must remain independent of the context window of the acting agent.

---

# Article XII — Self-Improvement Governance

## Law 12.1 — No silent production self-modification

No agent may silently promote changes to production prompts, skills, source adapters, policy, code, evaluation thresholds, or domain contracts.

## Law 12.2 — Changes follow an evaluation lifecycle

```text
Observation
→ Candidate Lesson
→ Candidate Change
→ Sandbox/Eval
→ Baseline Comparison
→ Human/Policy Review
→ Promote | Revise | Reject
→ Monitored Rollout
→ Rollback if necessary
```

## Law 12.3 — CEO may propose, not self-ratify

CEO Hermes may identify and prepare improvements but cannot unilaterally ratify changes that expand its own authority or alter constitutional policy.

---

# Article XIII — Fail-Closed Operation

## Law 13.1 — Ambiguity never creates authority

Missing/ambiguous policy, identity, tenant, scope, source, approval, or schema results in fail-closed behavior.

## Law 13.2 — Permitted degraded modes

When safe, systems may degrade to:

- read-only;
- bounded retry;
- partial result with uncertainty label;
- human escalation.

They may not invent missing authorization or evidence.

---

# Article XIV — Source and Version Lineage

## Law 14.1 — Source revisions are immutable events

External source updates create new immutable source snapshots rather than mutating previous source history.

## Law 14.2 — Material changes invalidate dependent assumptions

Eligibility, deadline, funding, requirement, geography, cancellation, or equivalent material source changes must trigger downstream re-evaluation according to the data constitution.

---

# Article XV — Interoperability Without Surrender

## Law 15.1 — Public standards are compatibility surfaces

CommonGrants and other standards may define interoperability mappings, but the platform retains richer internal contracts where required for evidence, workflow, matching, audit, and client functionality.

## Law 15.2 — External provider IDs are not internal sovereignty

Provider-specific IDs do not become internal primary identity by default.

---

# Article XVI — Authority Ladder

The platform recognizes:

- **L0 — OBSERVE:** read authorized state/evidence;
- **L1 — PROPOSE:** create plans/recommendations without governed mutation;
- **L2 — SAFE EXECUTE:** bounded internal research, parsing, matching, drafting, QA, and artifact generation;
- **L3 — MANAGED EXECUTE:** governed internal state mutation under policy/audit;
- **L4 — EXTERNAL ACTION:** externally visible communication/integration with required approval;
- **L5 — SUBMISSION / LEGALLY MATERIAL:** application submission, signing, certification, attestation, binding commitment.

Initial posture:

- Personal Hermes: L0–L1;
- CEO Hermes: L0–L2, with narrowly ratified L3 later;
- specialist workers: task-scoped L0/L2 only;
- deterministic services: only their predefined narrow mutation authority;
- L4/L5 disabled until future explicit ratification.

---

# Article XVII — Constitutional Change

Changes to constitutional law require:

1. explicit amendment/ADR ID;
2. rationale;
3. affected capability/domain analysis;
4. regression/adversarial tests;
5. review;
6. version increment;
7. rollback path where applicable.

No implementation detail may silently supersede a constitutional law.

---

# Provisional Ratification Conditions

This constitution becomes binding Book 1 v1.0 only when:

- Book 0 R0 Ratification passes;
- capability/authority machine-readable schemas are implemented;
- authority adversarial tests pass;
- zero unresolved P0 contradiction exists;
- approval and self-improvement policies are mapped to executable rules;
- Book 1 Reality Lock returns PASS.
