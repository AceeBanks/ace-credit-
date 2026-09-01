# Phase 1 IACER — Domain, Compliance, Security & MVP Foundation

## Intent

### Goal
Transform the organizational vision into an explicit system model that humans and coding agents can implement without inventing mission rules, entity boundaries, user roles, sensitive-data treatment, legal assumptions, or MVP scope.

### Mission / business reason
ACE Credit is expected to support real financial education, credit-related services, workforce/economic advancement, entrepreneurship, grant-funded nonprofit delivery, commercial services, and eventually participant-facing technology. These activities cross legal, operational, data, and organizational boundaries. Phase 1 creates the control plane before those boundaries are embedded in software.

### Primary beneficiaries
- Black women participating in nonprofit programs.
- Staff delivering nonprofit services.
- Commercial clients of the separate for-profit entity.
- Program leadership and administrators.
- Community and referral partners.
- Grant/funding and impact staff.
- Coding and operations agents working within approved permissions.

### Non-goals
Phase 1 does not:
- launch production participant services;
- automate credit disputes or consumer communications;
- choose a permanent AI runtime solely because one is currently installed;
- ingest real consumer reports or participant PII into development systems;
- implement payment processing;
- decide unresolved legal questions without qualified review;
- build a public participant application before the staff and governance model is stable.

## Abstraction

### Terms that must have one meaning

**Organization:** ACE Credit ecosystem at the strategy level; not itself a legal entity.

**Entity:** a legally distinct organization operating within the ecosystem, initially the nonprofit and for-profit.

**Tenant:** a security/data partition in software. A tenant generally maps to one legal entity unless an ADR explicitly permits another model.

**Program:** a defined service intervention operated by one entity, with eligibility, services, outcomes, funding constraints, dates, and staffing.

**Cohort:** a group of program enrollments managed together for delivery/reporting.

**Person:** a human identity record. A person may have different entity-specific roles or relationships but cross-entity identity linking must never imply cross-entity data access.

**Participant:** a person enrolled in a nonprofit program.

**Client:** a person or business receiving for-profit services.

**Case:** a bounded service-management record attached to an enrollment or client engagement, not a universal dossier.

**Enrollment:** the participant-program relationship, including eligibility status, dates, consent state, service plan, completion/exit, and reporting context.

**Service:** a delivered unit of program activity such as education, coaching, credit education, referral, business-readiness support, or another approved intervention.

**Goal:** a participant/client objective with owner, baseline, target, tasks, evidence, status, and time horizon.

**Outcome:** a measured change or milestone connected to a person/enrollment/program and supported by provenance.

**Referral:** a controlled handoff or recommendation to an external/internal resource, with minimum necessary data sharing.

**Credit workflow:** an approved process involving credit education, report review, credit-building planning, or another legally reviewed credit-related service.

**Agent:** an AI runtime/worker identity acting under a scoped policy, not a human employee and not an authority source.

**Agent run:** one bounded execution with an initiating user/system event, tools, inputs, outputs, approvals, and audit record.

**Approval:** an explicit human authorization for a defined consequential action; approval is not implied by access.

### Core business rules
1. Every operational record belongs to a legal entity/tenant.
2. Every program belongs to exactly one operating entity.
3. Shared technology does not create shared ownership of funds, contracts, or participant/client records.
4. Cross-entity access is denied by default and must have explicit legal/business justification, permission, and auditability.
5. Participant data collection must be purpose-limited and minimized.
6. Sensitive survivor information receives heightened access restrictions.
7. Agents receive capabilities, not blanket trust.
8. Consequential actions require an approval record before execution.
9. Compliance uncertainty blocks automation of the uncertain action, not unrelated low-risk work.
10. Outcomes must retain provenance: who/what recorded them, when, source type, and whether self-reported or independently verified.
11. Credit score is one possible metric, not a definition of economic stability.
12. Entrepreneurship is optional and must not become an assumed participant outcome.

### Decisions requiring owner approval
- mission/population change;
- nonprofit vs. for-profit boundary change;
- regulated credit-service scope;
- participant eligibility policy;
- production collection of credit-report data;
- external automated communications;
- production AI write permissions;
- cross-entity data sharing;
- retention/deletion policy;
- deployment of high-risk integrations;
- changes to human approval gates.

### Research-needed items
- exact launch jurisdiction(s) and state-specific credit-services requirements;
- nonprofit credit-services legal structure;
- for-profit credit-services pricing/contract model and applicable restrictions;
- consumer-report access method and permissible-purpose requirements before any direct bureau/provider integration;
- debt-management scope and licensing requirements before offering debt-management services;
- final privacy/retention schedule;
- insurance requirements;
- charitable-registration jurisdictions;
- production hosting/data-processing vendor requirements.

## Context

### Current repository state
- Root repository is the ACE Credit source of truth.
- Hermes Agent and Hermes WebUI are already present and operational on the current development setup.
- Root governance must control ACE Credit work; nested `hermes-webui/AGENTS.md` controls changes made inside that imported/runtime subtree and does not supersede the ACE Credit constitution.
- OpenClaw remains a candidate operations runtime and may be evaluated through an adapter/proof-of-concept rather than entangled directly with business logic.

### Architectural context
The planned platform contains four separable layers:
1. **Domain/application layer:** people, entities, programs, enrollments, cases, goals, outcomes, grants, approvals, audit events.
2. **Policy/control layer:** authorization, entity boundaries, approval gates, data classification, retention, compliance constraints.
3. **Integration layer:** messaging, storage, credit-data providers, payroll/HR, CRM/partners, grant/funder sources, identity providers.
4. **Agent/runtime layer:** Hermes, OpenClaw, coding agents, scheduled workers, model providers.

The agent/runtime layer may call approved application capabilities; it must not become the direct system of record for participant or financial operations.

### Data context
Anticipated information includes identity/contact data, financial education assessments, goals, income/employment information, housing status, survivor-sensitive information, financial/debt information, credit-related data, business information, program eligibility, referrals, documents, notes, grant/funder data, staff activity, and agent/audit events.

### Compliance/security context
Potentially applicable areas include consumer reporting, credit repair/credit services, telemarketing, debt management, consumer protection, nonprofit/tax rules, charitable solicitation, employment, privacy/security, grant compliance, contracts, conflicts/related-party transactions, accessibility, records retention, and vendor data processing.

The repository documents compliance requirements as issues to resolve and design controls to enforce. It does not substitute for qualified counsel.

## Expectations

### Functional
Phase 1 documentation must let a coding agent answer:
- what entity owns this workflow/data?
- who can perform/view/change it?
- what state transitions are valid?
- what data class is involved?
- what human approval is required?
- what compliance question must be resolved first?
- is this MVP, later, or prohibited for now?
- what audit event is required?

### Security/privacy
- deny cross-tenant access by default;
- no production secrets or PII in GitHub;
- synthetic data for development;
- RBAC plus context/entity checks;
- immutable or append-oriented audit history for consequential actions;
- explicit consent/authorization records where required;
- minimize survivor-sensitive visibility;
- secure file-storage abstraction before sensitive uploads;
- encrypted transport and appropriate encryption at rest in production;
- secret manager/environment isolation rather than repository credentials;
- revocable agent/service credentials.

### Human approval gates
At minimum, human approval is required before:
- external credit dispute/consumer communication;
- account changes based on regulated financial conclusions;
- grant application submission or certification;
- external legal/contractual acceptance;
- payment/money movement;
- deletion of protected production records outside established retention workflow;
- cross-entity disclosure of protected data;
- production access-policy changes;
- autonomous participant-facing advice outside approved educational content;
- publication of impact claims without data review.

### Observability/audit
Each consequential event should eventually capture:
- event ID and timestamp;
- entity/tenant;
- human/service/agent actor;
- action type;
- target object;
- before/after or event payload reference where appropriate;
- policy/permission basis;
- approval ID where applicable;
- originating request/run;
- integration destination;
- success/failure state;
- correlation ID.

### Agent expectations
- read the root constitution before ACE Credit work;
- use IACER for material tasks;
- operate least privilege;
- never treat memory as authoritative when repository policy differs;
- record sources for external research;
- surface uncertainty rather than fabricate rules;
- keep runtime-specific state outside business-domain tables unless represented through an adapter contract;
- produce reviewable diffs and tests.

### Quality bar
All Phase 1 deliverables must distinguish `DECIDED`, `WORKING ASSUMPTION`, `RESEARCH NEEDED`, `OPEN QUESTION`, and `FUTURE IDEA`. Architecture choices must include rationale, rejected alternatives, consequences, and revisiting triggers.

## Results

Phase 1 produces:
- [ ] `docs/architecture/DOMAIN_MAP.md`
- [ ] `docs/architecture/SYSTEM_CONTEXT.md`
- [ ] `docs/architecture/ADR-0001-agent-runtime-boundary.md`
- [ ] `docs/architecture/ADR-0002-entity-tenancy-boundary.md`
- [ ] `docs/architecture/REPOSITORY_STRUCTURE.md`
- [ ] `docs/security/DATA_CLASSIFICATION.md`
- [ ] `docs/security/THREAT_MODEL.md`
- [ ] `docs/compliance/COMPLIANCE_REGISTER.md`
- [ ] `docs/compliance/CREDIT_SERVICES_MATRIX.md`
- [ ] `docs/operations/APPROVAL_MATRIX.md`
- [ ] `docs/product/ACTORS_AND_ROLES.md`
- [ ] `docs/product/USER_JOURNEYS.md`
- [ ] `docs/product/MVP_SCOPE.md`
- [ ] `docs/impact/OUTCOME_MODEL.md`
- [ ] `.github/ISSUE_TEMPLATE/iacer-task.md`
- [ ] `.github/pull_request_template.md`
- [ ] README updated to point to current phase and governing documents
- [ ] unresolved compliance questions are explicit rather than embedded as assumptions
- [ ] architecture is implementable without choosing Hermes or OpenClaw as the permanent source of truth

## Phase 1 exit gate
Phase 1 is ready for owner review when every result above exists and no MVP-critical workflow requires a coding agent to make an unstated legal, entity, data-access, or human-approval decision.

## Status
`DECIDED`: mission, IACER governance, entity separation, governance-first architecture, runtime neutrality, human approval for consequential actions.

`WORKING ASSUMPTION`: one platform codebase may serve both entities through strict tenancy and policy boundaries.

`RESEARCH NEEDED`: launch-state credit-services law, consumer-report integrations, debt-management scope, retention schedule, production vendors.

`OPEN QUESTION`: final pilot jurisdiction, exact commercial service catalog, first production cohort size, and whether OpenClaw is used in addition to Hermes after adapter testing.
