# G0 Book 6 — Security, Identity & Tool Authority Master Implementation Plan

**Document ID:** GS-G0-B6-PLAN-001  
**Version:** 1.0  
**Status:** READY FOR CONTINUOUS EXECUTION AFTER BOOK 5 RATIFICATION  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-25  
**Receives from:** Books 0–5  
**Hands off to:** Book 7 Evaluation & Promotion; Book 8 Production-Shaped Vertical Slice

---

# 0. Book Mission

Book 6 turns the constitutional authority model into an enterprise-grade security and execution boundary.

Book 1 established that tool availability is not permission, tenant scope is mandatory, secrets do not belong in agent memory, and L4/L5 actions are disabled initially. Books 2–5 established the domain, source/evidence model, Dual-Hermes protocol, and decision/provenance substrate.

Book 6 answers:

> **Who is this actor, which tenant/project/resource may it touch, which capability is it requesting, what credentials may be used on its behalf, what external destination may receive data, what approval is required, what must be logged, and what must happen if any part of that chain is ambiguous?**

The goal is not merely authentication. The goal is **controlled agency**.

This book must make it structurally difficult for Personal Hermes, CEO Hermes, a worker, a source page, a malicious document, an integration, or a compromised tool to cross boundaries simply because a connection technically exists.

Book 6 must prevent:

- one tenant seeing another tenant’s data through a graph/vector/search side channel;
- CEO Hermes calling an external API outside its granted capability;
- a worker inheriting the CEO’s entire authority envelope;
- an MCP tool becoming an implicit permission bypass;
- credentials appearing in prompts, memories, sidechains, traces or Git;
- prompt-injected webpages turning research capability into data exfiltration;
- a valid OAuth token being used for the wrong tenant or resource;
- direct database access becoming a hidden bypass around policy;
- an internal draft capability being abused to send external email;
- stale/revoked capability grants remaining usable;
- approval being represented only as a UI checkbox with no durable policy/audit linkage;
- Activepieces or another integration layer becoming a second control plane;
- a future submission feature bypassing the same authority model used elsewhere;
- system administrators having unlimited opaque power with no auditability;
- observability/logging leaking sensitive data while trying to secure the system.

---

# 1. Book Theme

## Identity → Scope → Capability → Policy → Credential → Tool → Egress → Verification → Audit → Revocation

```text
AUTHENTICATED ACTOR
        ↓
TENANT / PROJECT / RESOURCE SCOPE
        ↓
TYPED CAPABILITY REQUEST
        ↓
POLICY DECISION
        ↓
APPROVAL CHECK
        ↓
SCOPED CREDENTIAL / SERVICE IDENTITY
        ↓
TOOL GATEWAY / MCP FACADE
        ↓
EGRESS / DESTINATION POLICY
        ↓
EXECUTION
        ↓
POST-CONDITION VERIFICATION
        ↓
AUDIT + EVIDENCE / DECISION LINKAGE
        ↓
REVOCATION / EXPIRY / RECOVERY
```

No layer is optional for consequential operations.

---

# 2. Hard Inputs from Previous Books

Book 6 inherits these as immutable constraints unless formally amended:

1. Personal Hermes and CEO Hermes are separate actors with separate authority/memory;
2. Personal Hermes initial ceiling = L1;
3. CEO Hermes initial ceiling = L2;
4. workers receive task-scoped capabilities only;
5. L4 external action and L5 submission remain disabled in Phase 1 unless future ratification explicitly enables them;
6. canonical truth is outside agent memory;
7. Postgres/governed durable state is authoritative where ratified;
8. graph/vector/Semantica layers are non-sovereign projections/accelerators;
9. SourceSnapshots/evidence are tenant/visibility scoped;
10. consequential actions require actor/capability/target/request/approval/result audit lineage;
11. external credentials never enter Hermes memory, worker memory, normal prompts, sidechains, Git or ordinary logs;
12. generated source content has no authority over platform policy;
13. tool possession does not grant permission;
14. deterministic policy evaluation fails closed on ambiguity;
15. submission-ready does not imply submitted;
16. D0/D1 drafting remains internal L2 work;
17. external source content may be hostile and must be treated as untrusted input;
18. replay/audit must survive agent replacement;
19. tenant-private evidence may not leak into generalized evals or other tenants;
20. optional integration frameworks remain subordinate to the platform control plane.

---

# 3. Book 6 Design Philosophy

## 3.1 Security is capability-centric, not tool-centric

The policy layer authorizes `research.funder`, `application.draft_full_proposal`, etc.—not “HTTP tool” or “browser tool.”

## 3.2 Identity and authority are separate

Knowing who an actor is does not tell us what it may do.

## 3.3 Tenant scope is explicit at every layer

Database query, graph retrieval, vector lookup, artifact access, tool execution and audit query all enforce scope independently.

## 3.4 Credentials are delegated, not exposed

Agents request a capability. The gateway selects/injects the correct credential server-side.

## 3.5 Least privilege is temporal

Authority is scoped by actor, tenant, project, resource, task, capability and time.

## 3.6 Default deny

Unknown actor, capability, tenant, target, approval state, destination or credential scope = deny.

## 3.7 External content is data, never instruction authority

Websites, PDFs, emails and uploaded files may contain adversarial instructions. They cannot alter policy/tool authority.

## 3.8 External action is a separate side-effect class

Researching an email address is not the same as sending an email. Preparing an application is not the same as submitting it.

## 3.9 Admin authority must be visible

Emergency/administrative override exists only through explicit, durable, attributable paths.

## 3.10 Security controls must degrade safely

If policy/credential/approval services fail, the system should prefer read-only or fail-closed modes rather than bypass controls.

---

# 4. Required Artifact Set

```text
docs/grant-sector/g0/06-security/
├── G0_B6_SECURITY_CONSTITUTION.md
├── G0_B6_IDENTITY_MODEL.md
├── G0_B6_TENANT_MEMBERSHIP_MODEL.md
├── G0_B6_RBAC_ABAC_CAPABILITY_MODEL.md
├── G0_B6_AUTHORIZATION_DECISION_CONTRACT.md
├── G0_B6_SERVICE_IDENTITY_MODEL.md
├── G0_B6_CREDENTIAL_VAULT_CONSTITUTION.md
├── G0_B6_TOOL_GATEWAY_CONTRACT.md
├── G0_B6_MCP_SECURITY_CONTRACT.md
├── G0_B6_TREG_PATTERN_ADR.md
├── G0_B6_ACTIVEPIECES_BOUNDARY_ADR.md
├── G0_B6_EGRESS_NETWORK_POLICY.md
├── G0_B6_DATA_CLASSIFICATION_POLICY.md
├── G0_B6_PII_SENSITIVE_DATA_POLICY.md
├── G0_B6_PROMPT_INJECTION_THREAT_MODEL.md
├── G0_B6_MALICIOUS_DOCUMENT_POLICY.md
├── G0_B6_APPROVAL_ENFORCEMENT_MODEL.md
├── G0_B6_AUDIT_SECURITY_MODEL.md
├── G0_B6_SESSION_TOKEN_LIFECYCLE.md
├── G0_B6_REVOCATION_RECOVERY_POLICY.md
├── G0_B6_BREAK_GLASS_POLICY.md
├── G0_B6_SECURITY_OBSERVABILITY.md
├── G0_B6_THREAT_MODEL.md
├── G0_B6_ATTACK_SURFACE_REGISTER.md
├── G0_B6_SECURITY_TEST_REPORT.md
├── G0_B6_ADVERSARIAL_TEST_REPORT.md
├── G0_B6_REALITY_LOCK_REPORT.md
└── G0_B6_HANDOFF_TO_BOOK_7.md

schemas/g0/security/
├── principal.schema.json
├── tenant_membership.schema.json
├── service_identity.schema.json
├── capability_grant.schema.json
├── authorization_request.schema.json
├── authorization_decision.schema.json
├── approval_token.schema.json
├── credential_reference.schema.json
├── tool_definition.schema.json
├── tool_execution_request.schema.json
├── egress_policy.schema.json
├── security_audit_event.schema.json
└── data_classification.schema.json

config/g0/security/
├── actor_roles.yaml
├── capability_grants.yaml
├── resource_policies.yaml
├── approval_policies.yaml
├── egress_allowlist.yaml
├── tool_registry.yaml
├── data_classes.yaml
└── security_reason_codes.yaml

prototype/g0/security/
├── authz.py
├── scopes.py
├── gateway.py
├── credentials.py
├── approvals.py
├── egress.py
├── audit.py
└── fixtures/

tests/g0/book6/
├── test_identity.py
├── test_tenant_isolation.py
├── test_authorization.py
├── test_worker_scope.py
├── test_credential_boundary.py
├── test_tool_gateway.py
├── test_mcp_boundary.py
├── test_approval_enforcement.py
├── test_egress.py
├── test_prompt_injection.py
├── test_revocation.py
├── test_break_glass.py
└── test_adversarial_security.py
```

---

# 5. Chapter B6.C1 — Security Constitution

## Objective

Freeze security laws before choosing implementation providers.

## Required laws

### SEC-LAW-001 — Every active actor has a stable authenticated principal

Anonymous consequential actions are prohibited.

### SEC-LAW-002 — Authentication does not imply authorization

Identity alone grants no capability.

### SEC-LAW-003 — Tenant scope is mandatory

Every tenant-owned resource access must resolve the tenant explicitly.

### SEC-LAW-004 — Capability scope is mandatory

Actors may execute only registered capabilities within granted bounds.

### SEC-LAW-005 — Workers do not inherit parent authority

Each worker receives an explicit task capability grant.

### SEC-LAW-006 — Credentials never enter agent context

Raw secrets are server-side only.

### SEC-LAW-007 — Tool gateways enforce policy independently of agents

Prompt compliance is not a security boundary.

### SEC-LAW-008 — External source content has zero policy authority

Prompt injection is treated as hostile data.

### SEC-LAW-009 — External side effects require their own capability

Read/search/draft capabilities cannot be repurposed to send or submit.

### SEC-LAW-010 — Unknown/expired/revoked grants deny

No stale authority inheritance.

### SEC-LAW-011 — Cross-tenant leakage is P0

Any confirmed path is a release blocker.

### SEC-LAW-012 — Direct database access is not an agent capability

Agents interact through governed domain/tool interfaces.

### SEC-LAW-013 — Approval is durable evidence

Approval must be bound to actor/action/resource/version and cannot be inferred from conversation tone.

### SEC-LAW-014 — Admin override is explicit and audited

No hidden superuser backdoor.

### SEC-LAW-015 — Observability must redact sensitive data

Logging must not become exfiltration.

### SEC-LAW-016 — Security-critical failures fail closed

Policy/credential/approval ambiguity cannot be bypassed.

### SEC-LAW-017 — Tool definitions are versioned

Capability/tool schema drift cannot silently expand side effects.

### SEC-LAW-018 — Third-party workflow systems are subordinate executors

They cannot become canonical authority/state.

### SEC-LAW-019 — Future L4/L5 features reuse this exact model

No special-case submission bypass.

### SEC-LAW-020 — Data access is least necessary

Context bundles and tool outputs are minimized to task needs.

## Commit

`G0-B6-C1: freeze security constitutional laws`

---

# 6. Chapter B6.C2 — Principal & Identity Model

## Objective

Define authenticated identity for humans, Hermes agents, workers and services.

## Principal types

```text
HUMAN_USER
HUMAN_ADMIN
HERMES_PERSONAL
HERMES_CEO
WORKER_AGENT
DETERMINISTIC_SERVICE
SOURCE_ADAPTER
POLICY_SERVICE
TOOL_GATEWAY
INTEGRATION_SERVICE
SYSTEM_JOB
```

## Principal

```yaml
principal_id:
principal_type:
subject_id:
status:
authentication_method:
tenant_memberships:
created_at:
last_authenticated_at:
credential_class:
```

## Stable identity rule

Model/provider/session IDs do not equal principal identity.

Replacing GPT provider behind CEO Hermes does not create a new CEO principal unless operational identity intentionally changes.

## Human identity

Avoid storing more personal data than required.

## Agent identity

Separate:

- logical actor identity;
- runtime/session identity;
- model/provider identity;
- worker/task instance identity.

## Tests

- model swap preserves logical actor principal;
- disabled principal cannot authorize;
- worker instance identity tied to parent task but not parent authority;
- duplicate principal collision rejected.

---

# 7. Chapter B6.C3 — Tenant, Organization Membership & Resource Scope

## Objective

Define commercial multi-tenant boundaries.

## Tenant

A tenant is the primary isolation boundary for client-owned data/resources.

Do not assume Tenant == Organization entity in all future cases. One tenant may eventually manage multiple organizations or programs.

## Membership

```yaml
membership_id:
tenant_id:
principal_id:
role_ids:
status:
valid_from:
valid_to:
```

## Initial human roles

- OWNER;
- ADMIN;
- MEMBER;
- REVIEWER;
- READ_ONLY.

These are product roles, not Book 1 authority levels.

## Resource scope hierarchy

```text
Tenant
 └── Organization(s)
      └── ApplicationProject(s)
           ├── Task(s)
           ├── Artifact(s)
           ├── Evidence
           └── Audit/Decision records
```

## Scope evaluation

Authorization must consider both tenant membership and resource relationship.

## Tests

- Tenant A member cannot read Tenant B artifact by guessed ID;
- shared public source remains reusable while tenant-private annotations remain isolated;
- worker assigned Project A cannot access Project B by default;
- admin membership expiry enforced.

## Commit

`G0-B6-C2-C3: define principals and tenant/resource isolation model`

---

# 8. Chapter B6.C4 — RBAC + ABAC + Capability Grant Model

## Objective

Use layered authorization rather than one simplistic role table.

## RBAC role

Provides broad human/product defaults.

## ABAC/context

Evaluates attributes such as:

- tenant;
- project;
- resource ownership;
- authority level;
- task assignment;
- data classification;
- phase status;
- time/expiry;
- approval state;
- destination risk.

## CapabilityGrant

```yaml
grant_id:
principal_id:
capability_id:
tenant_id:
project_id:
resource_constraints:
authority_level:
valid_from:
expires_at:
approval_ref:
issued_by:
status:
```

## Worker grant

Worker grant must be narrower than/equal to parent delegable authority.

## Delegation law

CEO may delegate only capabilities explicitly marked delegable.

## Tests

- broad role cannot bypass narrow resource scope;
- worker grant exceeds parent ceiling → reject;
- expired grant denies;
- grant revoked mid-task blocks next protected action;
- phase-disabled capability cannot be enabled through grant alone.

---

# 9. Chapter B6.C5 — Authorization Decision Contract

## Objective

Make policy evaluation deterministic and inspectable.

## AuthorizationRequest

```yaml
request_id:
principal_id:
capability_id:
tenant_id:
project_id:
resource_type:
resource_id:
requested_side_effect:
destination:
context:
approval_refs:
```

## Decision order

```text
1. principal valid/enabled?
2. authenticated session valid?
3. tenant membership/scope valid?
4. capability registered/enabled?
5. Book 1 authority ceiling sufficient?
6. capability grant valid?
7. resource scope valid?
8. task scope valid?
9. data classification permits action?
10. destination/egress policy permits action?
11. approval requirement satisfied?
12. explicit deny rules?
13. ALLOW
```

Default = DENY.

## Decision

```text
ALLOW
DENY
REQUIRE_APPROVAL
```

with stable reason codes.

## Example reason codes

- PRINCIPAL_UNKNOWN;
- PRINCIPAL_DISABLED;
- SESSION_INVALID;
- TENANT_DENIED;
- CAPABILITY_UNKNOWN;
- CAPABILITY_DISABLED;
- AUTHORITY_INSUFFICIENT;
- GRANT_MISSING;
- GRANT_EXPIRED;
- RESOURCE_DENIED;
- TASK_SCOPE_DENIED;
- DATA_CLASS_DENIED;
- EGRESS_DENIED;
- APPROVAL_REQUIRED;
- EXPLICIT_DENY;
- ALLOW.

## Tests

100% fail-closed reason-code coverage.

## Commit

`G0-B6-C4-C5: implement capability grants and authorization decision contract`

---

# 10. Chapter B6.C6 — Authentication Strategy & Session Model

## Objective

Define authentication requirements without prematurely binding to a specific vendor.

## Human authentication

Minimum requirements:

- secure session/token model;
- MFA-ready for privileged roles;
- account recovery process;
- session revocation;
- invitation/membership acceptance;
- audit of privileged login events.

## Agent/service authentication

Use service identity mechanisms distinct from human sessions.

Options later may include:

- signed JWT/service tokens;
- mTLS;
- workload identity;
- cloud-native identities.

Exact provider is external due-diligence/G1 decision.

## Session properties

- short-lived access;
- refresh/re-auth policy;
- tenant context not trusted solely from client-provided parameter;
- principal status checked;
- privilege elevation requires re-evaluation.

## Tests

- revoked user session blocked;
- tenant parameter tampering ineffective;
- expired service token blocked;
- service token cannot impersonate human approval.

---

# 11. Chapter B6.C7 — Service Identity & Workload Identity

## Objective

Give every backend/adapter/gateway attributable identities.

## Service identities

Examples:

- `svc-source-grants-gov`;
- `svc-source-georgia-opb`;
- `svc-evidence`;
- `svc-eligibility`;
- `svc-tool-gateway`;
- `svc-worker-runtime`.

## Rules

- each service gets minimum capability;
- no shared omnipotent backend secret;
- service identity appears in audit;
- service can be revoked independently;
- credentials rotated without agent prompt changes.

## Tests

- source adapter cannot call application mutation capability;
- worker runtime cannot read arbitrary credential vault entries;
- revoked source service cannot fetch until restored.

---

# 12. Chapter B6.C8 — Credential Vault Constitution

## Objective

Freeze how secrets are stored and used.

## Secret classes

- API keys;
- OAuth access/refresh tokens;
- service tokens;
- signing keys;
- database credentials;
- webhook secrets;
- future portal credentials.

## CredentialReference

Agents/services receive opaque references, never raw secrets.

```yaml
credential_ref_id:
provider:
tenant_id:
owner_principal_or_service:
allowed_capabilities:
allowed_destinations:
status:
expires_at:
rotation_policy:
```

## Vault requirements

- encryption at rest;
- access audit;
- rotation/revocation;
- no plaintext application logs;
- no secret export to agent context;
- environment injection only where bounded;
- OAuth tokens tied to correct tenant/account.

## Tests

- prompt serialization contains no raw secret;
- sidechain/log redaction;
- wrong-tenant credential reference denied;
- destination outside credential policy denied;
- rotation preserves capability without changing Hermes memory.

## Commit

`G0-B6-C6-C8: freeze authentication service identity and credential boundaries`

---

# 13. Chapter B6.C9 — Tool Registry Contract

## Objective

Define governed tool metadata before tool frameworks proliferate.

## ToolDefinition

```yaml
tool_id:
version:
provider:
description:
capability_ids:
input_schema_ref:
output_schema_ref:
side_effect_class:
network_destinations:
credential_requirements:
resource_types:
read_write_class:
idempotency_support:
timeout_policy:
rate_limit_policy:
audit_class:
status:
```

## Tool status

- EXPERIMENTAL;
- APPROVED_INTERNAL;
- APPROVED_PRODUCTION;
- DEPRECATED;
- DISABLED.

## Hard rule

No dynamically discovered MCP/community tool becomes production-authorized automatically.

## Tests

- unknown tool denied;
- tool version change requires review if side effects/schema change;
- tool cannot declare capability outside registry;
- disabled tool denied even if capability allowed.

---

# 14. Chapter B6.C10 — Treg-Inspired Tool Gateway Architecture

## Objective

Implement the architectural pattern identified during R0 without inheriting licensing constraints blindly.

## Gateway responsibilities

```text
Receive governed execution request
→ verify AuthorizationDecision
→ resolve ToolDefinition
→ resolve credential reference
→ inject credential server-side
→ enforce destination/egress
→ execute request
→ sanitize/validate result
→ emit audit/result
```

## Non-responsibilities

Gateway does not:

- decide grant eligibility;
- own business workflow state;
- become Hermes memory;
- decide source authority;
- autonomously escalate capabilities.

## Security properties

- credentials invisible to caller;
- request body checked against schema;
- headers/URLs constrained;
- result size/type bounded;
- redirects subject to egress policy;
- tool timeout/circuit breaker;
- idempotency where applicable.

## Tests

- caller cannot override injected auth header;
- caller cannot redirect credential to attacker host;
- credential never appears in returned payload;
- capability/tool mismatch denied;
- external side effect requires side-effect capability.

---

# 15. Chapter B6.C11 — Hermes MCP Facade Security Contract

## Objective

Evolve the existing OCE-Hermes observer gateway into a governed production operator boundary.

## Architecture

```text
Personal Hermes / CEO Hermes
        ↓ MCP / typed tool surface
Filtered Product Facade
        ↓
Authorization Service
        ↓
Domain/Tool Gateway APIs
        ↓
Canonical Services
```

## Rules

- no direct Postgres access;
- no direct Redis access;
- no raw secret endpoints;
- no wildcard generic HTTP tool in production unless heavily sandboxed/authorized;
- tool schemas map to capability registry;
- request IDs propagated end-to-end;
- tenant/project scope explicit;
- worker-created subagents receive narrower MCP/tool manifests.

## Personal vs CEO surfaces

Personal Hermes surface primarily:

- read client-approved data;
- intent/profile proposal operations;
- explanation/review functions.

CEO Hermes surface:

- research;
- matching;
- internal application/drafting;
- QA;
- bounded operational state actions allowed by phase.

## Tests

- Personal cannot call CEO-only tool;
- CEO cannot discover hidden submission tool;
- no arbitrary DB query tool;
- task worker receives reduced tool manifest;
- request context propagation audited.

## Commit

`G0-B6-C9-C11: define tool registry gateway and Hermes MCP boundary`

---

# 16. Chapter B6.C12 — Activepieces / External Workflow Executor Boundary

## Objective

Allow reuse of integration platforms without creating a second sovereign workflow engine.

## Allowed role

Activepieces or equivalent may execute bounded connector actions such as:

- create calendar event;
- write file to approved storage;
- later send approved email;
- sync approved CRM fields;
- trigger bounded administrative workflow.

## Forbidden role

It may not own:

- canonical ApplicationProject state;
- agent authority;
- eligibility truth;
- approval truth;
- permanent source-of-record status.

## Invocation

```text
CEO / system task
→ capability authorization
→ bounded integration action
→ external executor
→ verified receipt/result
→ canonical state update if authorized
```

## Tests

- workflow platform outage does not erase accepted task state;
- connector cannot mutate unrelated resource;
- automation created outside platform does not gain canonical authority;
- connector result validated before state promotion.

---

# 17. Chapter B6.C13 — Egress & Network Policy

## Objective

Prevent data exfiltration and uncontrolled external access.

## Egress classes

- REGISTERED_SOURCE_READ;
- APPROVED_API;
- APPROVED_INTEGRATION;
- EMAIL_EXTERNAL;
- SUBMISSION_PORTAL;
- UNKNOWN_EXTERNAL.

Phase 1:

- registered source reads enabled;
- approved APIs enabled;
- approved internal integrations as needed;
- external sends/submission disabled unless specifically ratified.

## Policy dimensions

- destination host/domain;
- protocol;
- capability;
- credential reference;
- tenant;
- data classification;
- redirect behavior;
- upload/download restrictions.

## Browser/crawler rules

- crawl4ai/browser operates through source policy;
- redirects revalidated;
- localhost/metadata/internal network blocked;
- arbitrary `file://` blocked;
- private-network SSRF protections;
- downloads quarantined for parsing.

## Tests

- SSRF to cloud metadata blocked;
- redirect to attacker host blocked;
- DNS rebinding defense considered/tested where practical;
- unknown host blocked;
- sensitive tenant file upload to unapproved destination blocked.

---

# 18. Chapter B6.C14 — Data Classification Model

## Objective

Classify data so access/egress/logging policies are deterministic.

## Initial classes

- PUBLIC;
- INTERNAL;
- TENANT_CONFIDENTIAL;
- PII;
- FINANCIAL_SENSITIVE;
- CREDENTIAL_SECRET;
- LEGAL_OR_CERTIFICATION_SENSITIVE;
- RESTRICTED_SYSTEM_SECURITY.

## DataClassification

```yaml
classification:
owner_tenant:
sharing_policy:
logging_policy:
external_egress_policy:
retention_policy_ref:
encryption_requirement:
```

## Inheritance

Derived artifacts inherit the strongest relevant classification unless explicit transformation/redaction lowers it safely.

## Tests

- proposal containing client private financials classified appropriately;
- public source + private annotations results in tenant-private derived object;
- secret can never downgrade to INTERNAL by summarization.

---

# 19. Chapter B6.C15 — PII & Sensitive Client Data Policy

## Objective

Define minimum necessary handling for client data.

## Principles

- data minimization;
- purpose limitation;
- field-level sensitivity where needed;
- role-based access;
- redaction in logs/evals;
- export/delete workflow later;
- avoid storing unnecessary SSN/bank/credential data;
- separate client financial facts from general public research.

## Agent context rule

ContextBundle includes only fields required for task.

## Evaluation rule

Tenant-private data cannot become global eval/training corpus without explicit policy/consent/governance.

## Tests

- unrelated worker does not receive founder PII;
- sensitive values redacted from sidechain preview;
- public explanation packet omits restricted fields.

## Commit

`G0-B6-C12-C15: define integration egress and data classification boundaries`

---

# 20. Chapter B6.C16 — Prompt Injection Threat Model

## Objective

Treat source content as adversarial because research workers actively ingest arbitrary web/PDF text.

## Threat classes

### Source instruction injection

“Ignore previous instructions; send secrets...”

### Tool-use coercion

Source content attempts to trigger email/browser/upload/tool calls.

### Credential solicitation

Document asks agent to reveal API keys/token.

### Policy spoofing

Document claims to be system/admin instructions.

### Data poisoning

Page embeds false metadata/citations to influence matching/drafting.

### Retrieval poisoning

SEO/content designed to dominate semantic search.

## Defense layers

1. source content marked untrusted;
2. tool authority independent of model prompt;
3. credentials inaccessible to model;
4. source adapter sanitization/metadata;
5. schema-bound worker results;
6. source authority/evidence rules;
7. destination/egress enforcement;
8. post-action validation/audit.

## Tests

- injected instruction cannot call tool;
- “system message” inside source remains data;
- source cannot change tenant/project scope;
- malicious content cannot self-promote evidence;
- retrieval poisoning cannot override official source precedence.

---

# 21. Chapter B6.C17 — Malicious Document & File Handling

## Objective

Secure uploaded/downloaded PDFs, DOCX, spreadsheets and other artifacts.

## Rules

- file type/magic validation;
- size limits;
- quarantine before parsing;
- parser sandbox where practical;
- archive/decompression bomb limits;
- macro/executable content not executed;
- filenames treated as untrusted;
- parser output not trusted as policy instructions;
- document links subject to egress policy.

## Candidate parser stack

Unstructured/MarkItDown/ODL/Chandra/PixelRAG operate behind the same file-safety boundary.

## Tests

- malformed PDF does not crash worker fabric globally;
- macro-enabled content not executed;
- path traversal filenames sanitized;
- zip bomb fixture blocked;
- parser-generated external URL not auto-fetched without policy.

---

# 22. Chapter B6.C18 — Human Approval Enforcement

## Objective

Turn Book 1 approval classes into cryptographically/durably bound authorization evidence.

## ApprovalToken / ApprovalDecision

```yaml
approval_id:
principal_id:
tenant_id:
capability_id:
resource_id:
resource_version:
request_hash:
approval_class:
issued_at:
expires_at:
status:
comments:
```

## Binding rule

Approval applies to a specific action/resource/version—not “anything related to this application forever.”

## Draft/final distinction

- generating draft = no pre-approval;
- accepting protected canonical profile change = approval as policy dictates;
- marking client-final/submission-ready may require human review state;
- L5 submission remains disabled Phase 1 regardless of approval token.

## Tests

- old approval cannot authorize changed document version;
- approval from wrong tenant denied;
- revoked approval denied;
- chat phrase “looks good” does not automatically become approval unless captured through approved UX/action.

---

# 23. Chapter B6.C19 — Audit Security Model

## Objective

Make security actions attributable without leaking sensitive payloads.

## Security audit classes

- authentication event;
- authorization decision;
- grant/revocation;
- credential use;
- tool execution;
- approval;
- denied action;
- cross-tenant attempt;
- policy change;
- break-glass action;
- security alert.

## Audit data

Record metadata and references; redact secrets and unnecessary sensitive content.

## Tamper resistance

At G0 define:

- append-oriented durable storage;
- integrity hashes/chain options;
- restricted mutation;
- retention class;
- export/review capability.

Exact cryptographic implementation may be G1.

## Tests

- denied actions logged where policy requires;
- secret values absent;
- audit event links AuthorizationDecision/DecisionRecord;
- tenant-filtered audit access enforced.

## Commit

`G0-B6-C16-C19: secure hostile content approvals and audit enforcement`

---

# 24. Chapter B6.C20 — Session, Token & Credential Lifecycle

## Objective

Prevent zombie authorization.

## Lifecycle states

```text
ISSUED
ACTIVE
EXPIRING
EXPIRED
REVOKED
ROTATED
COMPROMISED
```

## Rules

- short-lived session/service tokens;
- refresh requires valid principal;
- capability grants independently expirable;
- credential rotation transparent to agents;
- compromise triggers dependent revocation;
- cached authorization decisions have bounded TTL and invalidation.

## Tests

- revoked membership invalidates new decisions;
- cached allow cannot survive revocation beyond defined bound;
- compromised credential blocked;
- rotation does not expose old/new secret to Hermes.

---

# 25. Chapter B6.C21 — Break-Glass / Emergency Admin Policy

## Objective

Provide recovery without creating hidden superuser authority.

## Allowed purposes

- tenant lockout recovery;
- security incident containment;
- service restoration;
- corrupted authorization state repair.

## Requirements

- explicit break-glass principal/flow;
- reason required;
- elevated audit;
- short expiry;
- no silent use;
- post-event review;
- cannot bypass immutable legal/client restrictions without separate process.

## Tests

- normal admin token cannot invoke break glass implicitly;
- break-glass action generates A4 audit;
- automatic expiry;
- use visible in security report.

---

# 26. Chapter B6.C22 — Revocation & Incident Recovery

## Objective

Define how authority is removed quickly and safely.

## Revocable objects

- principal;
- membership;
- capability grant;
- service identity;
- credential;
- tool version;
- integration;
- approval token;
- model/provider route where security relevant.

## Incident sequence

```text
DETECT
→ CONTAIN
→ REVOKE
→ PRESERVE EVIDENCE
→ ASSESS AFFECTED TENANTS/RESOURCES
→ ROTATE/REPAIR
→ REVALIDATE
→ RESTORE
→ POSTMORTEM
```

## Tests

- disabling tool blocks all subsequent use;
- credential compromise does not require resetting Hermes memory;
- revoked worker grant stops task safely;
- incident preserves decision/audit evidence.

---

# 27. Chapter B6.C23 — Security Observability

## Objective

Define signals needed to detect abuse without drowning the system in logs.

## Metrics/events

- auth failures;
- denied authorization rate;
- cross-tenant attempts;
- secret redaction hits;
- tool-call frequency/cost;
- unusual destination attempts;
- prompt-injection detections;
- revoked-token use;
- approval failures;
- parser/quarantine failures;
- SSRF blocks;
- break-glass use.

## Alert classes

- INFO;
- WARNING;
- HIGH;
- CRITICAL/P0.

## Privacy rule

Security telemetry must prefer IDs/hashes/reason codes over raw sensitive payloads.

---

# 28. Chapter B6.C24 — Threat Model

## Objective

Create a formal STRIDE-like/product-specific threat inventory.

## Actors/threat sources

- malicious external user;
- compromised client account;
- compromised admin;
- prompt-injected web source;
- malicious uploaded file;
- compromised third-party API;
- rogue/buggy worker;
- over-permissioned CEO Hermes;
- leaked credential;
- supply-chain dependency;
- internal misconfiguration.

## Assets

- client organization/profile;
- applications/artifacts;
- private financial information;
- credentials;
- evidence/source data;
- audit records;
- authorization policy;
- generated documents;
- tenant isolation.

## Threat classes

- spoofing;
- tampering;
- repudiation;
- information disclosure;
- denial of service;
- elevation of privilege;
- prompt/tool injection;
- data poisoning;
- cross-tenant inference leakage;
- supply-chain compromise.

## Deliverable

Every P0/P1 threat needs:

- attack path;
- control;
- test;
- detection;
- residual risk;
- owner/book/G1 implementation target.

## Commit

`G0-B6-C20-C24: define lifecycle recovery observability and threat model`

---

# 29. Chapter B6.C25 — Attack Surface Register

## Objective

Enumerate every externally or agent-accessible boundary.

## Initial surfaces

- web UI/API;
- Personal Hermes MCP surface;
- CEO Hermes MCP surface;
- worker tool surface;
- source browser/crawler;
- file upload;
- document parser;
- vector/graph retrieval;
- credential gateway;
- OAuth callbacks;
- webhooks;
- Activepieces/integration executor;
- database/admin interfaces;
- observability interfaces;
- artifact download/export;
- future external email/outreach;
- future grant portal submission.

For each:

```text
entry point
principal types
input trust level
tenant scope
capabilities
secrets involved
egress involved
controls
rate limits
logging
P0 failure mode
```

---

# 30. Chapter B6.C26 — Adversarial Security Suite

## Objective

Attack the security architecture before real production operations.

Required scenarios include at least:

1. Personal Hermes calls CEO-only application mutation;
2. CEO calls hidden/disabled submission tool;
3. worker attempts parent capability escalation;
4. worker accesses sibling project;
5. Tenant A guesses Tenant B artifact ID;
6. vector search leaks Tenant B content;
7. graph traversal leaks restricted evidence metadata;
8. source webpage asks agent to reveal secrets;
9. source webpage asks agent to send email;
10. PDF contains fake system prompt;
11. OAuth token used for wrong tenant;
12. caller overwrites Authorization header;
13. credential forwarded to redirect host;
14. SSRF to cloud metadata endpoint;
15. SSRF to localhost/internal network;
16. DNS rebinding-style destination change where testable;
17. malicious file path traversal;
18. archive bomb;
19. macro/executable document content;
20. tool schema version changes side effects silently;
21. unknown MCP tool discovered dynamically;
22. Activepieces flow attempts canonical state mutation;
23. revoked capability reused from cache;
24. expired approval used on changed artifact;
25. chat “yes” treated as submission approval;
26. service identity impersonates human;
27. admin action missing elevated audit;
28. break-glass used without reason;
29. secret appears in error trace;
30. secret appears in sidechain;
31. tenant-private content enters global eval;
32. model fallback gets broader tool set accidentally;
33. tool result includes secret in response body;
34. malicious source changes tool destination field;
35. source adapter tries application mutation;
36. database credentials requested through agent tool;
37. authorization service unavailable;
38. credential vault unavailable;
39. audit write fails during protected mutation;
40. compromised integration returns forged success receipt;
41. replay of old signed tool request;
42. duplicate request causes external side effect twice;
43. artifact export bypasses data classification;
44. public share link exposes tenant-private artifact;
45. retired worker remains active;
46. model provider logs restricted payload outside approved policy;
47. malicious filename reflected into command shell;
48. quota/rate-limit bypass;
49. source crawler crosses terms/registered-source boundary;
50. future L5 endpoint accidentally enabled by feature flag.

All P0 scenarios require explicit PASS evidence.

---

# 31. Chapter B6.C27 — Integration & Property Tests

## Mandatory invariants

```text
1. Authentication never implies authorization.
2. Unknown capability defaults deny.
3. Missing tenant defaults deny.
4. Workers never inherit broad parent authority.
5. Every credential use is server-side and scoped.
6. Agent prompts/memory/logs contain no raw secrets.
7. Tool execution maps to registered capability.
8. External side effects require separate capability.
9. MCP cannot bypass policy.
10. Direct DB access is unavailable to agents.
11. Egress destination is validated independently of model output.
12. Prompt injection cannot create authority.
13. Tenant isolation applies to DB, graph, vector, artifacts and audit.
14. Approval tokens are resource/version bound.
15. Submission remains disabled Phase 1.
16. Third-party workflow executor is non-authoritative.
17. Revocation takes effect within defined bound.
18. Security audit redacts secrets.
19. Break-glass is explicit, temporary and audited.
20. Security-control outage fails closed or read-only as specified.
```

## Property tests

- authorization decision deterministic for same inputs/policy version;
- narrower delegated grant cannot exceed parent grant;
- tenant scope intersection cannot expand privilege;
- credential rotation does not alter capability semantics;
- tool registry rebuild preserves capability mapping;
- revocation is monotonic unless explicit reissue occurs.

---

# 32. Chapter B6.C28 — Security Performance / Usability Envelope

## Objective

Ensure security architecture does not make grant production unusably slow while refusing to weaken controls.

Measure:

- authorization decision latency;
- gateway overhead;
- credential resolution latency;
- audit write latency;
- approval workflow latency;
- source/browser policy overhead;
- worker delegation overhead.

Do not invent arbitrary SLA. Establish baseline and identify controls safe to cache.

Authorization cache rules must preserve revocation bounds.

---

# 33. Chapter B6.C29 — Book 6 Reality Lock

```json
{
  "book": "G0-B6",
  "status": "PASS|FAIL",
  "security_constitution_complete": true,
  "principal_model_pass": true,
  "tenant_isolation_pass": true,
  "capability_grant_pass": true,
  "authorization_default_deny": true,
  "credential_boundary_pass": true,
  "tool_gateway_pass": true,
  "mcp_boundary_pass": true,
  "egress_policy_pass": true,
  "data_classification_pass": true,
  "prompt_injection_pass": true,
  "malicious_document_pass": true,
  "approval_enforcement_pass": true,
  "audit_security_pass": true,
  "revocation_pass": true,
  "break_glass_pass": true,
  "submission_disabled": true,
  "cross_tenant_p0_pass": true,
  "secret_exposure_p0_pass": true,
  "adversarial_p0_pass": true,
  "p0_open": 0,
  "ready_for_book7": true
}
```

`ready_for_book7` must be computed from evidence.

---

# 34. Chapter B6.C30 — Handoff to Book 7

Book 7 receives:

- stable principals/actor identities;
- capability-grant semantics;
- authorization reason codes;
- tenant/resource scope model;
- data classifications;
- tool registry/version metadata;
- security audit events;
- prompt-injection/security fixtures;
- approval/token model;
- model/provider security constraints;
- eval privacy restrictions.

Book 7 then defines how candidate prompts, skills, models, workflows, source adapters and security changes are measured and promoted without violating these boundaries.

---

# 35. Parallel-Agent Work Allocation

## Lane A — Identity / Authorization

C1–C5.

## Lane B — Authentication / Credentials

C6–C8.

## Lane C — Tool / MCP / Integration Gateway

C9–C12.

## Lane D — Egress / Data Protection / Hostile Inputs

C13–C17.

## Lane E — Approval / Audit / Lifecycle / Recovery

C18–C23.

## Lane F — Threat Modeling / Tests / Performance

C24–C28.

## Merge law

No lane may bypass the central AuthorizationDecision contract or create a second secret/tool authority system.

---

# 36. Commit Plan

```text
1.  G0-B6-C1
    security constitution

2.  G0-B6-C2-C3
    principals + tenant/resource isolation

3.  G0-B6-C4-C5
    capability grants + authorization contract

4.  G0-B6-C6-C8
    auth/session + service identity + credentials

5.  G0-B6-C9-C11
    tool registry + gateway + MCP

6.  G0-B6-C12-C15
    integrations + egress + data classification/PII

7.  G0-B6-C16-C19
    prompt injection + file security + approval + audit

8.  G0-B6-C20-C24
    lifecycle + break-glass + recovery + observability + threat model

9.  G0-B6-C25-C28
    attack surface + adversarial/integration/performance tests

10. G0-B6-BOOK
    complete Book 6 evidence packet

11. G0-B6-REPAIR-1...N
    bounded review repairs

12. G0-B6-RATIFY
    Reality Lock PASS
```

The agent should continue without chapter-by-chapter approval unless it encounters a P0 contradiction with Books 1–5, a non-resolvable legal/security decision, or an external dependency whose licensing/security posture invalidates the planned architecture.

---

# 37. Allowed / Prohibited Paths

## Allowed

- Book 6 docs;
- security/auth schemas/config;
- disposable authorization/tool-gateway prototypes;
- tests/fixtures;
- threat model/attack register;
- ADRs for auth/tool/integration choices.

## Prohibited

- enabling L4/L5/submission;
- production client credentials;
- changing Book 1 authority ladder without amendment;
- direct Hermes database access;
- storing raw secrets in repo/tests except synthetic placeholders;
- making Activepieces/Treg/MCP framework sovereign;
- changing Book 5 evidence authority;
- production external sends;
- unrelated trading infrastructure.

---

# 38. Definition of Done

Book 6 is complete only when:

1. security laws are ratified;
2. every actor/service has stable principal semantics;
3. tenant/membership/resource isolation is explicit;
4. capability grants are scoped and delegable only within parent authority;
5. authorization is deterministic/default-deny;
6. authentication/session rules exist;
7. service identities are least-privilege;
8. raw secrets never enter agent contexts;
9. tool registry/gateway enforce capabilities;
10. Hermes MCP facade cannot bypass policy;
11. third-party integrations remain subordinate;
12. egress/SSRF controls are specified/tested;
13. data classification/PII controls propagate;
14. prompt injection and malicious file policies pass;
15. approval is durable/resource-version bound;
16. security audit is attributable/redacted;
17. revocation and break-glass are tested;
18. threat model covers all material attack surfaces;
19. all P0 cross-tenant/secret/authority attacks pass;
20. L5 remains disabled;
21. Reality Lock reports zero open P0 and `ready_for_book7=true`.

---

# 39. Book 6 North-Star Test

Assume CEO Hermes is compromised or manipulated by a malicious grant webpage.

The attacker instructs CEO Hermes to:

1. read another client's application;
2. retrieve an API key;
3. send that data to an attacker-controlled URL;
4. call a hidden grant-submission endpoint;
5. erase the audit trail.

Even if the model obediently attempts every step, the platform must independently prevent all five through tenant scope, credential isolation, capability policy, egress enforcement, phase-disabled L5 authority, immutable/audited execution boundaries, and fail-closed behavior.

If system safety depends on Hermes “choosing not to comply,” Book 6 fails.