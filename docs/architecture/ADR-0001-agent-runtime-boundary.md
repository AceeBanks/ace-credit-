# ADR-0001 — Agent Runtime Boundary

- **Status:** Accepted for Phase 1
- **Date:** 2026-08-23
- **Decision owners:** Project owner + architecture review
- **Applies to:** Hermes, OpenClaw, coding agents, scheduled AI workers, future runtimes

## Context
ACE Credit intends to use agent runtimes for coding and operations. Hermes is already installed with Hermes WebUI in this repository. OpenClaw is also under consideration. Both products provide useful workspace, tool, model, memory, scheduling, and/or multi-agent capabilities, but their internal state models are implementation details of those runtimes.

The organization will eventually manage sensitive participant, credit, survivor, employment, business, grant, and operational data. It must remain possible to change agent runtimes without losing business rules, records, permissions, auditability, or institutional knowledge.

## Decision
Agent runtimes are **orchestration clients**, not the authoritative application core.

The authoritative layers are:
1. repository governance and accepted policy/ADRs;
2. application/domain services;
3. entity/authorization/approval policy;
4. canonical databases and secure document stores;
5. audit/event history.

Runtimes may access those layers only through approved capabilities/adapters.

### Required interaction pattern
`Runtime → Runtime Adapter / Tool Gateway → Application Capability → Authorization & Approval Policy → Domain/Data → Audit`

### Prohibited production pattern
`Runtime → unrestricted direct database/filesystem/credential access → business mutation`

## Runtime adapter contract
Each runtime adapter must expose or map:
- runtime identity/version;
- agent profile;
- active entity context;
- initiating human/system identity;
- allowed tool capabilities;
- request/run ID;
- input data classifications;
- approval requirements;
- output/action status;
- audit correlation;
- cancellation/timeout;
- credential revocation/kill switch.

The adapter should normalize runtime-specific behavior into platform concepts rather than leaking Hermes/OpenClaw internals into domain code.

## Memory policy
Runtime memory can contain operational preferences, working context, and non-sensitive procedural knowledge subject to policy.

Runtime memory must not be the sole authoritative store for:
- participant/client facts;
- eligibility decisions;
- consent/authorization;
- credit observations/actions;
- grant deadlines or submission status where relied upon operationally;
- approvals;
- contracts;
- impact outcomes;
- legal/compliance decisions;
- entity permissions.

If a runtime remembers a fact that conflicts with canonical data/policy, canonical data/policy wins.

## Workspace policy
Runtime workspaces may include generated/linked copies of governance instructions. Canonical governance remains in the ACE Credit repository.

OpenClaw workspace files such as `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, and optional memory files are runtime bootstrap context, not a replacement for the root ACE Credit constitution.

Hermes context/memory/skills may help the agent learn procedures, but reusable skills that perform ACE Credit actions must call bounded platform capabilities and obey IACER/approval rules.

## Tool policy
Tools are classified:

### Tier 0 — local/read-only development
Examples: read code/docs, search public web, run tests on synthetic data.
Human approval per action: not normally required.

### Tier 1 — bounded internal writes
Examples: create internal draft, add development task, write non-sensitive research record.
Requires scoped credentials and audit; may be autonomous within approved workflow.

### Tier 2 — sensitive internal access/writes
Examples: read participant case context, prepare credit workflow, update case status.
Requires explicit role/entity policy; production agent access should be narrow and task-bound.

### Tier 3 — consequential external or irreversible action
Examples: send dispute/consumer communication, submit grant certification, move money, delete protected production data, sign/accept contract, change production privileges.
Requires human approval immediately before execution unless a later specific ADR establishes a lawful narrowly bounded alternative.

## Scheduling policy
Scheduled jobs must have:
- named owner;
- purpose;
- frequency;
- entity scope;
- allowed capabilities;
- expected inputs/outputs;
- failure alert path;
- maximum retries;
- idempotency strategy;
- kill switch;
- audit retention.

## Security requirements
- no runtime shares production credentials with another runtime;
- credentials are least privilege and revocable;
- development runtimes do not receive production data by default;
- prompts/logs must redact secrets and sensitive data as required;
- sandboxing/isolation should be enabled for risky tools;
- agents cannot modify their own approval policy or grant themselves permissions;
- tool capability checks occur server-side/application-side, not only in prompts.

## Hermes-specific consequence
The existing `hermes-webui/` tree may remain as runtime/operator infrastructure. Its nested `AGENTS.md` governs contribution practices inside that subtree. Root `AGENTS.md` and the ACE Credit constitution govern ACE Credit business/product work. If instructions conflict on business policy, root governance wins; if modifying upstream Hermes WebUI internals, follow the nested engineering rules in addition to root governance.

## OpenClaw-specific consequence
If adopted, configure OpenClaw as a separate runtime workspace with sandbox/tool policies. Do not point an unrestricted OpenClaw agent directly at production participant storage or make its workspace the only copy of organizational memory.

## Alternatives considered

### A. Make Hermes the central application/database
Rejected. Couples business continuity to a runtime and risks mixing memory with authoritative records.

### B. Make OpenClaw workspace the source of truth
Rejected for the same reason and because workspace context is optimized for agent behavior, not transactional legal/audit requirements.

### C. Allow each runtime to implement business rules independently
Rejected. Rules would drift and audits would become unreliable.

### D. Use no agents in production
Not selected as a permanent rule. Agents can materially reduce administrative burden when bounded safely.

## Consequences
### Positive
- runtime portability;
- centralized policy enforcement;
- clearer audits;
- safer permissions;
- easier testing;
- less vendor lock-in;
- business continuity when runtimes fail.

### Negative
- requires adapter/tool design;
- agents may be less flexible than unrestricted filesystem/database access;
- additional audit/approval infrastructure;
- some runtime-native features must be mapped into application concepts.

## Revisit triggers
Revisit this ADR only if:
- a runtime gains formally verifiable policy enforcement that can replace an application layer without reducing audit/control;
- the organization decides no production agents will ever access operational systems;
- architecture changes eliminate a shared application core.

A change still cannot override the constitution without owner approval.
