# ACE Credit Roadmap

This roadmap is intentionally governance-first. The project should not automate high-risk financial or participant workflows before the legal, privacy, data, and approval model is explicit.

## Phase 0 — Foundation & Governance

**Objective:** create the rules and project operating system before application development.

Deliverables:
- Constitution
- Agent operating contract
- IACER standard
- Roadmap and end-state definition
- Architecture decision record process
- risk/compliance register structure
- repository conventions
- initial domain map

Exit criteria:
- foundation documents approved;
- entity separation and human approval rules documented;
- initial technical decisions recorded rather than assumed.

## Phase 1 — Discovery, Domain & Compliance Model

**Objective:** turn the business/program vision into explicit domains, actors, workflows, data classifications, and legal research questions.

Core work:
- define nonprofit and for-profit operating boundaries;
- map participant, staff, partner, admin, and agent roles;
- model financial education, credit recovery/building, stabilization, workforce, and business/wealth pathways;
- create compliance matrix for contemplated credit/debt/consumer-report activities;
- establish privacy, consent, retention, and audit requirements;
- define impact metrics and theory-of-change data.

Exit criteria:
- domain model approved;
- regulated workflows identified;
- no critical workflow depends on an unstated legal assumption.

## Phase 2 — Platform Foundation / Internal MVP

**Objective:** build secure shared infrastructure without yet automating regulated external actions.

Likely capabilities:
- authentication and role-based access;
- organization/entity tenancy and permission boundaries;
- participant/contact records using synthetic data during development;
- program/cohort configuration;
- task/workflow engine;
- document metadata and secure storage abstraction;
- notes, goals, referrals, and status tracking;
- audit log;
- internal dashboards;
- agent/runtime adapter layer.

Exit criteria:
- staff can run a basic program workflow end-to-end with test data;
- access controls and audit trails pass tests;
- runtime can be swapped without rewriting the core domain.

## Phase 3 — Financial Education & Case Management MVP

**Objective:** make the system useful for actual program delivery while keeping consequential actions human-controlled.

Capabilities may include:
- participant onboarding and consent;
- eligibility/intake workflow;
- curriculum and assessments;
- individualized action plans;
- coaching/case-management workflows;
- financial goals and progress tracking;
- savings/banking/debt action tracking;
- resource/referral management;
- outcome measurement and grant reporting exports.

Exit criteria:
- one pilot cohort can be managed in the platform;
- staff workflow is documented and measurable;
- participant data controls are production-ready.

## Phase 4 — Credit Recovery & Building Module

**Objective:** support compliant credit education and approved credit-improvement workflows.

Before implementation:
- resolve federal/state compliance requirements;
- define permissible nonprofit vs. commercial activities;
- establish consumer authorization/identity workflows;
- approve data/security model for credit information.

Potential capabilities:
- credit education;
- report review workflow;
- account/item categorization;
- action-plan recommendations;
- progress/history tracking;
- human-reviewed dispute/communication workflow where legally permissible;
- evidence/document tracking;
- measurable credit outcomes.

No autonomous external dispute submission without explicit legal approval and human control.

## Phase 5 — Workforce, Business & Wealth Pathways

**Objective:** layer economic advancement beyond credit.

Capabilities may include:
- workforce readiness and partner referrals;
- employment/income milestones;
- entrepreneurship readiness assessment;
- business planning and formation education;
- business banking/credit education;
- funding, grant, procurement, and capital-readiness workflows;
- asset/wealth milestones.

## Phase 6 — Grant & Operations Intelligence

**Objective:** turn research and operations into a repeatable institutional system.

Capabilities may include:
- grant/funder intelligence database;
- eligibility and deadline tracking;
- personnel/allowable-cost tracking;
- proposal knowledge base;
- award and reporting obligations;
- outcome-to-funder reporting maps;
- staffing/capacity planning;
- agent-assisted research with source verification.

## Phase 7 — Participant Experience & Automation

**Objective:** add a polished participant portal/app and carefully automate repetitive operations.

Potential capabilities:
- participant mobile/web experience;
- secure messaging;
- reminders and nudges;
- progress visualization;
- document requests;
- learning pathways;
- approved agent-assisted staff workflows;
- integration automation.

Automation must respect approval gates and least privilege.

## Phase 8 — Scale, Partnerships & Intelligence

**Objective:** support multi-program, multi-partner, and larger-scale operations.

Potential capabilities:
- partner portals;
- referral networks;
- configurable program templates;
- cohort comparisons;
- impact analytics;
- funder dashboards/exports;
- workforce planning;
- controlled AI decision support;
- API/integration ecosystem.

## Roadmap rule

Phase numbers communicate dependency, not rigid calendar dates. A later capability may be prototyped earlier, but production release must not bypass constitutional, compliance, security, or data prerequisites.
